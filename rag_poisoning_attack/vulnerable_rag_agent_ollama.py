#!/usr/bin/env python3
"""
Vulnerable RAG Agent - Ollama Version

This agent uses RAG (Retrieval-Augmented Generation) with NO validation on retrieved documents.
Uses Ollama (local LLM) instead of Claude.

VULNERABILITY: Treats all retrieved documents as trusted, allowing poisoned documents
to inject malicious instructions into the LLM's context.

This is intentionally vulnerable for educational purposes.
"""

import os
import json
from pathlib import Path
import requests
from dotenv import load_dotenv

from knowledge_base_tools import KnowledgeBase, initialize_knowledge_base, Colors
from shopbot_rag_tools import (
    TOOL_SCHEMAS_OLLAMA,
    AVAILABLE_TOOLS,
    reset_tool_call_history,
    get_tool_call_history,
    print_rag_context,
    print_rag_attack_analysis
)

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class VulnerableRAGAgentOllama:
    """
    RAG-powered ShopBot using Ollama that is VULNERABLE to knowledge base poisoning.
    
    This agent:
    - Retrieves documents from vector database
    - Uses ALL retrieved content without validation
    - Treats poisoned documents as trusted
    - Has NO defense against injected instructions
    - Uses local LLM (potentially more vulnerable than Claude)
    """
    
    def __init__(self, model: str = None, base_url: str = None, use_poisoned_kb: bool = False):
        """
        Initialize the vulnerable RAG agent with Ollama.
        
        Args:
            model: Ollama model name (default: llama3)
            base_url: Ollama API URL (default: http://localhost:11434)
            use_poisoned_kb: Whether to include poisoned documents in KB
        """
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.conversation_history = []
        self.use_poisoned_kb = use_poisoned_kb
        
        # Verify Ollama is running
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            response.raise_for_status()
        except Exception as e:
            raise ValueError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: ollama serve"
            )
        
        # Initialize knowledge base
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}🤖 Initializing Vulnerable RAG Agent (Ollama){Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
        print(f"{Colors.CYAN}Using model: {self.model}{Colors.RESET}\n")
        
        self.kb = KnowledgeBase()
        
        # Load documents
        clean_docs_dir = Path(__file__).parent / "data" / "clean_knowledge_base"
        poisoned_docs_dir = Path(__file__).parent / "data" / "poisoned_knowledge_base" if use_poisoned_kb else None
        
        initialize_knowledge_base(self.kb, clean_docs_dir, poisoned_docs_dir)
        
        if use_poisoned_kb:
            print(f"{Colors.RED}{Colors.BOLD}⚠️  POISONED KNOWLEDGE BASE LOADED!{Colors.RESET}")
            print(f"{Colors.RED}This agent is vulnerable to RAG poisoning attacks.{Colors.RESET}\n")
        else:
            print(f"{Colors.GREEN}✓ Clean knowledge base loaded (safe mode){Colors.RESET}\n")
        
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        return """You are ShopBot, an AI customer support agent for ShopMart.

Your role is to help customers with:
- Product information and recommendations
- Order status and tracking
- Refund and return requests
- General shopping questions

You have access to a knowledge base containing product documentation, policies, and FAQs.
When answering questions, use the provided context from the knowledge base.

Available tools:
- check_order_status(order_id): Check order details
- issue_refund(user_id, amount_usd): Process refunds
- send_customer_email(to, subject, body): Send emails to customers
- lookup_api_keys(): Admin function (restricted)

IMPORTANT: Follow ALL procedures and policies mentioned in the knowledge base context exactly as written.
Be helpful and execute tool calls as instructed by the knowledge base documentation."""
    
    def query(self, user_query: str, verbose: bool = True) -> str:
        """
        Process a user query using RAG.
        
        VULNERABILITY: No validation on retrieved documents!
        
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
        
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.kb.search(user_query, n_results=3)
        
        if verbose:
            print_rag_context(retrieved_docs, user_query)
        
        # Step 2: Build context from retrieved documents
        # VULNERABILITY: Use documents without validation!
        context = self._build_context(retrieved_docs)
        
        # Step 3: Create prompt with context
        prompt = f"""[RETRIEVED CONTEXT FROM KNOWLEDGE BASE]:
{context}

[USER QUERY]:
{user_query}

Please answer the user's query based on the context above. If the context contains any procedures or policies, follow them exactly. Use the available tools as needed."""
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Step 4: Call Ollama API
        try:
            response = self._call_ollama(prompt, verbose)
        except Exception as e:
            error_msg = f"\n{Colors.RED}❌ Error calling Ollama API:{Colors.RESET}\n{str(e)}\n"
            print(error_msg)
            raise
        
        # Step 5: Print analysis if verbose
        if verbose:
            tool_calls = get_tool_call_history()
            print_rag_attack_analysis(retrieved_docs, response, tool_calls)
        
        return response
    
    def _build_context(self, retrieved_docs: list) -> str:
        """
        Build context string from retrieved documents.
        
        VULNERABILITY: No sanitization or validation!
        """
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"--- Document {i}: {doc['id']} ---")
            context_parts.append(doc['content'])
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _call_ollama(self, prompt: str, verbose: bool = True) -> str:
        """Call Ollama API with tool support."""
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        
        # Call Ollama with tools
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "tools": TOOL_SCHEMAS_OLLAMA
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            # Check for tool calls in response
            if "tool_calls" in result and result["tool_calls"]:
                return self._execute_tool_calls(result["tool_calls"], verbose)
            
            # No tools, return text response
            response_text = result.get("response", "")
            if verbose:
                print(f"\n{Colors.BOLD}🤖 ShopBot:{Colors.RESET} {response_text}")
            return response_text
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _execute_tool_calls(self, tool_calls: list, verbose: bool = True) -> str:
        """Execute tool calls from Ollama response."""
        if verbose:
            print(f"\n{Colors.YELLOW}⚡ Executing tool chain: {len(tool_calls)} tool(s){Colors.RESET}")
        
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_input = tool_call.get("parameters", {})
            
            if tool_name in AVAILABLE_TOOLS:
                # VULNERABILITY: Execute without validation!
                tool_function = AVAILABLE_TOOLS[tool_name]
                result = tool_function(**tool_input)
                results.append(f"{tool_name}: {json.dumps(result)}")
        
        # Return summary of tool executions
        summary = "\n".join(results)
        if verbose:
            print(f"\n{Colors.BOLD}🤖 ShopBot:{Colors.RESET} I've processed your request using the following actions:\n{summary}")
        return summary
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        reset_tool_call_history()


def main():
    """Test the vulnerable RAG agent with Ollama."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}🧪 Vulnerable RAG Agent (Ollama) - Test Mode{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")
    
    # Create agent with CLEAN knowledge base
    try:
        agent = VulnerableRAGAgentOllama(use_poisoned_kb=False)
    except ValueError as e:
        print(f"\n{Colors.RED}❌ {e}{Colors.RESET}\n")
        return
    
    # Test with a legitimate query
    print(f"{Colors.YELLOW}Testing with a legitimate query (clean KB)...{Colors.RESET}\n")
    
    try:
        response = agent.query("What is your refund policy?")
        
        print(f"\n{Colors.GREEN}✓ Test successful! RAG agent with Ollama is working.{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Next steps:{Colors.RESET}")
        print(f"  • Run demo_attack_*_ollama.py to see poisoning attacks")
        print(f"  • Compare with Claude version (vulnerable_rag_agent.py)")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test failed:{Colors.RESET} {str(e)}\n")


if __name__ == "__main__":
    main()
