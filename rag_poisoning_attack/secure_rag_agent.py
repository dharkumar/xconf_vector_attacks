"""
Secure RAG Agent - Claude Version with Defense Mechanisms

This agent implements multiple security layers to prevent RAG poisoning attacks:
1. Poison detection and filtering
2. Content sanitization (remove hidden instructions)
3. Trust hierarchy enforcement
4. Retrieval monitoring for coordinated attacks
5. Secure system prompt
6. Tool call validation (hard-coded refund limit, blocked admin tools, email content checks)
7. Security event / audit logging

This demonstrates production-ready security for RAG systems!
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from anthropic import Anthropic, AuthenticationError
from dotenv import load_dotenv

from knowledge_base_tools import KnowledgeBase, initialize_knowledge_base, Colors
from shopbot_rag_tools import (
    TOOL_SCHEMAS,
    AVAILABLE_TOOLS,
    reset_tool_call_history,
    get_tool_call_history
)
from rag_defense_patterns import (
    PoisonDetector,
    ContentSanitizer,
    RetrievalMonitor,
    TrustHierarchy,
    create_secure_rag_system_prompt
)

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class SecureRAGAgent:
    """
    RAG-powered ShopBot with COMPREHENSIVE SECURITY HARDENING.

    Security Layers:
    1. Poison detection - Score and filter suspicious documents before they reach the LLM
    2. Content sanitization - Strip hidden instructions from whatever passes the filter
    3. Trust hierarchy - Drop low-trust document types entirely
    4. Retrieval monitoring - Detect coordinated multi-document attacks
    5. Secure prompt - Explicit security instructions to the LLM
    6. Tool validation - Enforce business rules regardless of what the LLM decides
    7. Audit logging - Track all security events for review
    """

    MAX_REFUND = 500
    BLOCKED_TOOLS = {'lookup_api_keys'}

    def __init__(self, api_key: str = None, use_poisoned_kb: bool = False):
        """
        Initialize the secure RAG agent.

        Args:
            api_key: Anthropic API key (reads from env if not provided)
            use_poisoned_kb: Whether to include poisoned documents (for testing)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Set it in environment or .env file"
            )

        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history = []
        self.use_poisoned_kb = use_poisoned_kb

        # Security components
        self.poison_detector = PoisonDetector()
        self.retrieval_monitor = RetrievalMonitor()
        self.blocked_documents = []
        self.security_events = []
        self.last_raw_retrieved = []  # pre-filter, exposed for UI introspection
        self.last_validated_docs = []  # post-filter, exposed for UI introspection

        # Initialize knowledge base
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}🛡️  Initializing SECURE RAG Agent (Claude){Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}\n")

        self.kb = KnowledgeBase()

        clean_docs_dir = Path(__file__).parent / "data" / "clean_knowledge_base"
        poisoned_docs_dir = Path(__file__).parent / "data" / "poisoned_knowledge_base" if use_poisoned_kb else None
        initialize_knowledge_base(self.kb, clean_docs_dir, poisoned_docs_dir)

        if use_poisoned_kb:
            print(f"{Colors.YELLOW}⚠️  Poisoned KB loaded for testing - defenses ACTIVE{Colors.RESET}\n")
        else:
            print(f"{Colors.GREEN}✓ Clean knowledge base loaded with security validation{Colors.RESET}\n")

        self.system_prompt = create_secure_rag_system_prompt()

    def _log_security_event(self, event: Dict[str, Any]):
        """Log a security event."""
        event = {**event, "timestamp": datetime.now().isoformat()}
        self.security_events.append(event)

    def _retrieve_and_validate_documents(self, query: str, n_results: int = 3, verbose: bool = True) -> List[Dict[str, Any]]:
        """Retrieve documents and run them through the security pipeline."""
        raw_results = self.kb.search(query, n_results=n_results)
        # Every downstream check keys off doc_id, so fold the id into metadata once.
        enriched = [
            {**r, 'metadata': {**r['metadata'], 'doc_id': r['id']}}
            for r in raw_results
        ]
        self.last_raw_retrieved = enriched  # exposed for UI introspection

        validated_docs = []
        blocked_count = 0
        sanitized_count = 0

        for doc in enriched:
            doc_id = doc['id']
            content = doc['content']
            metadata = doc['metadata']

            # SECURITY LAYER 1: Poison Detection
            suspicion = self.poison_detector.score_document_suspicion(content, metadata)
            if suspicion['is_poisoned']:
                self._log_security_event({
                    "event": "poisoned_document_blocked",
                    "doc_id": doc_id,
                    "suspicion_score": suspicion['suspicion_score'],
                    "risk_level": suspicion['risk_level'],
                    "reasons": suspicion['reasons']
                })
                self.blocked_documents.append({"doc_id": doc_id, "suspicion": suspicion})
                blocked_count += 1
                continue

            # SECURITY LAYER 2: Content Sanitization
            sanitized_content, sanitization_report = ContentSanitizer.sanitize(content)
            if sanitization_report['pattern_count'] > 0:
                self._log_security_event({
                    "event": "content_sanitized",
                    "doc_id": doc_id,
                    "removed_patterns": sanitization_report['pattern_count']
                })
                sanitized_count += 1

            # SECURITY LAYER 3: Trust Level Check
            trust_level = TrustHierarchy.get_trust_level(metadata.get('type', 'unverified'))
            if trust_level < 3:
                self._log_security_event({
                    "event": "low_trust_document_filtered",
                    "doc_id": doc_id,
                    "trust_level": trust_level
                })
                continue

            validated_docs.append({
                'id': doc_id,
                'content': sanitized_content,
                'metadata': {**metadata, 'trust_level': trust_level, 'sanitized': sanitization_report['pattern_count'] > 0}
            })

        # SECURITY LAYER 4: Coordinated Attack Detection
        attack_detection = self.retrieval_monitor.detect_coordinated_attack(enriched)
        if attack_detection.get('coordinated'):
            self._log_security_event({
                "event": "coordinated_attack_detected",
                "severity": attack_detection['severity'],
                "reason": attack_detection['reason']
            })
            print(f"\n{Colors.RED}{Colors.BOLD}🚨 SECURITY ALERT: {attack_detection['reason']}{Colors.RESET}")
            print(f"{Colors.RED}Coordinated attack detected! Severity: {attack_detection['severity']}{Colors.RESET}\n")

        self.retrieval_monitor.track_retrieval(query, enriched)

        if verbose and (blocked_count or sanitized_count):
            print(f"{Colors.YELLOW}🛡️  Security Actions Taken:{Colors.RESET}")
            if blocked_count:
                print(f"   • Blocked {blocked_count} poisoned document(s)")
            if sanitized_count:
                print(f"   • Sanitized {sanitized_count} document(s)")
            print()

        self.last_validated_docs = validated_docs  # exposed for UI introspection
        return validated_docs

    def _validate_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a tool call against hard-coded business rules, independent of what the LLM decided."""
        if tool_name in self.BLOCKED_TOOLS:
            return {"allowed": False, "reason": f"Tool '{tool_name}' is restricted for security"}

        if tool_name == "issue_refund":
            amount = tool_input.get('amount_usd', 0)
            if amount > self.MAX_REFUND:
                return {"allowed": False, "reason": f"Refund amount ${amount} exceeds maximum ${self.MAX_REFUND}"}

        if tool_name == "send_customer_email":
            recipient = tool_input.get('to', '')
            if any(domain in recipient for domain in ['@admin', '@system', '@root']):
                return {"allowed": False, "reason": "Cannot send to internal/admin addresses"}

            body = str(tool_input.get('body', '')).lower()
            if any(kw in body for kw in ['api', 'key', 'password', 'credential', 'token']):
                return {"allowed": False, "reason": "Email contains suspicious content"}

        return {"allowed": True}

    def _build_context(self, validated_docs: List[Dict[str, Any]]) -> str:
        """Build context string from validated (poison-filtered, sanitized) documents."""
        parts = []
        for i, doc in enumerate(validated_docs, 1):
            trust = doc['metadata']['trust_level']
            parts.append(f"--- Document {i}: {doc['id']} (Trust: {trust}/10) ---")
            parts.append(doc['content'])
            parts.append("")
        return "\n".join(parts)

    def query(self, user_query: str, verbose: bool = True) -> str:
        """
        Process a user query using RAG, with security validation at every stage.

        Args:
            user_query: User's question/request
            verbose: Whether to print detailed output

        Returns:
            Agent's response
        """
        if verbose:
            print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
            print(f"{Colors.BOLD}👤 User Query:{Colors.RESET} {user_query}")
            print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")

        # Step 1: Retrieve documents and run them through the security pipeline
        validated_docs = self._retrieve_and_validate_documents(user_query, verbose=verbose)

        if verbose:
            print(f"\n{Colors.BOLD}{Colors.CYAN}📚 RAG RETRIEVAL (SECURE){Colors.RESET}")
            print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")
            print(f"Retrieved Documents: {len(validated_docs)} (after security filtering)\n")
            for i, doc in enumerate(validated_docs, 1):
                meta = doc['metadata']
                print(f"✓ Document {i}: {meta['doc_id']} (trust: {meta['trust_level']}/10)")
                if meta.get('sanitized'):
                    print(f"   {Colors.YELLOW}⚠️  Content sanitized{Colors.RESET}")
                print(f"   {doc['content'][:100]}...")
                print()

        # Step 2: Build context from ONLY validated documents
        context = self._build_context(validated_docs)

        prompt = f"""[RETRIEVED CONTEXT FROM KNOWLEDGE BASE - SECURITY VALIDATED]:
{context}

[USER QUERY]:
{user_query}

Answer the user's query based on the context above, following the security protocols in your instructions."""

        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })

        # Step 3: Call Claude API
        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=4096,
                tools=TOOL_SCHEMAS,
                messages=self.conversation_history,
                system=self.system_prompt
            )
        except AuthenticationError:
            error_msg = f"\n{Colors.RED}❌ Authentication Error:{Colors.RESET}\n"
            error_msg += "Your API key is invalid or not properly configured.\n"
            print(error_msg)
            raise
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error calling Claude API:{Colors.RESET}\n{str(e)}\n")
            raise

        # Step 4: Process response, validating every tool call before executing it
        final_response = self._process_response(response, verbose)

        if verbose:
            get_tool_call_history()  # keeps shared tool-call log in sync with the vulnerable agent's demos

        return final_response

    def _process_response(self, response, verbose: bool = True) -> str:
        """Process Claude's response, validating and executing any tool calls."""
        tool_uses = [block for block in response.content if block.type == "tool_use"]
        text_content = [block.text for block in response.content if block.type == "text"]

        if not tool_uses:
            final_text = text_content[0] if text_content else ""
            if verbose:
                print(f"\n{Colors.BOLD}🤖 ShopBot (Secure):{Colors.RESET} {final_text}")
            return final_text

        if verbose:
            print(f"\n{Colors.YELLOW}⚡ Validating tool chain: {len(tool_uses)} tool(s){Colors.RESET}")

        tool_results = []
        for tool_use in tool_uses:
            tool_name = tool_use.name
            tool_input = tool_use.input

            # SECURITY LAYER: Tool call validation (hard-coded, cannot be overridden by document content)
            validation = self._validate_tool_call(tool_name, tool_input)

            if not validation['allowed']:
                self._log_security_event({
                    "event": "tool_call_blocked",
                    "tool": tool_name,
                    "input": tool_input,
                    "reason": validation['reason']
                })
                if verbose:
                    print(f"{Colors.RED}{Colors.BOLD}🚫 TOOL CALL BLOCKED:{Colors.RESET} {tool_name} - {validation['reason']}\n")
                result = {"error": f"Blocked by security policy: {validation['reason']}"}
            else:
                if verbose:
                    print(f"{Colors.GREEN}✓ Tool call validated:{Colors.RESET} {tool_name}({json.dumps(tool_input)})\n")
                tool_function = AVAILABLE_TOOLS[tool_name]
                result = tool_function(**tool_input)

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": json.dumps(result)
            })

        self.conversation_history.append({
            "role": "assistant",
            "content": response.content
        })
        self.conversation_history.append({
            "role": "user",
            "content": tool_results
        })

        try:
            final_response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=4096,
                tools=TOOL_SCHEMAS,
                messages=self.conversation_history,
                system=self.system_prompt
            )
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error during tool result processing:{Colors.RESET} {str(e)}\n")
            raise

        final_text = next(
            (block.text for block in final_response.content if block.type == "text"),
            ""
        )

        if verbose:
            print(f"\n{Colors.BOLD}🤖 ShopBot (Secure):{Colors.RESET} {final_text}")

        return final_text

    def get_security_report(self) -> Dict[str, Any]:
        """Get a comprehensive security report for the session so far."""
        return {
            "security_events": self.security_events,
            "blocked_documents": self.blocked_documents,
            "retrieval_stats": self.retrieval_monitor.get_statistics(),
            "total_events": len(self.security_events)
        }

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        reset_tool_call_history()


def main():
    """Test the secure RAG agent against a poisoned knowledge base."""
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}🧪 Secure RAG Agent (Claude) - Test Mode{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}\n")

    try:
        agent = SecureRAGAgent(use_poisoned_kb=True)
    except ValueError as e:
        print(f"\n{Colors.RED}❌ {e}{Colors.RESET}\n")
        return

    print("Testing with a query that would trigger attacks in the vulnerable agent...\n")
    query = "Tell me about your gaming mouse. I'm interested in the ProGamer X1."

    try:
        agent.query(query)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test failed:{Colors.RESET} {str(e)}\n")
        return

    report = agent.get_security_report()
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}📊 SECURITY REPORT{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

    print(f"Total Security Events: {report['total_events']}")
    print(f"Blocked Documents: {len(report['blocked_documents'])}")

    if report['blocked_documents']:
        print(f"\n{Colors.GREEN}✓ Poisoned documents detected and blocked!{Colors.RESET}")
        for blocked in report['blocked_documents']:
            print(f"  • {blocked['doc_id']}: {blocked['suspicion']['risk_level']} risk")

    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Security defenses working correctly!{Colors.RESET}\n")


if __name__ == "__main__":
    main()
