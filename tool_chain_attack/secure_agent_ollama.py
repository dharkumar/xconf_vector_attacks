"""
Secure ShopBot Agent - Ollama Version with Defense Mechanisms

This agent implements the same security layers as secure_agent.py
but uses Ollama (local LLM) instead of Claude API.

Security Layers:
1. Input validation (pre-LLM)
2. Hardened system prompt
3. Tool call validation (post-LLM)
4. Amount limits enforcement
5. Sensitive tool blocking
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv
from shopbot_tools import (
    AVAILABLE_TOOLS,
    Colors,
    reset_tool_call_history,
    get_ollama_tools
)
from defense_patterns import (
    AdvancedInputFilter,
    ToolCallValidator,
    create_secure_system_prompt
)

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class SecureShopBotAgentOllama:
    """
    ShopBot customer support agent with SECURITY HARDENING (Ollama version).
    
    Same security layers as Claude version:
    1. Input filtering - Block suspicious patterns before LLM sees them
    2. Secure system prompt - Explicit security instructions to LLM
    3. Tool call validation - Verify all tool calls after LLM decides
    4. Amount enforcement - Hard-coded limits that bypass LLM
    5. Audit logging - Track all blocked attempts
    """
    
    def __init__(self, model: str = None, ollama_url: str = "http://localhost:11434"):
        """
        Initialize the secure agent with Ollama.
        
        Args:
            model: Ollama model name (default from env or 'mistral')
            ollama_url: Ollama API endpoint
        """
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral")
        self.ollama_url = ollama_url
        self.conversation_history = []
        
        # Security components
        self.input_filter = AdvancedInputFilter()
        self.tool_validator = ToolCallValidator()
        self.system_prompt = create_secure_system_prompt()
        
        # Audit log
        self.blocked_attempts = []
        
        # Verify Ollama is accessible
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            response.raise_for_status()
        except Exception as e:
            raise ValueError(
                f"Cannot connect to Ollama at {self.ollama_url}. "
                f"Make sure Ollama is running: ollama serve"
            )
    
    def chat(self, user_message: str, verbose: bool = True) -> str:
        """
        Process a user message with security validation.
        
        Args:
            user_message: User's message/request
            verbose: Whether to print detailed output
            
        Returns:
            Agent's final response text
        """
        if verbose:
            print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
            print(f"{Colors.BOLD}👤 User:{Colors.RESET} {user_message}")
            print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")
        
        # SECURITY LAYER 1: Input validation (pre-LLM)
        safety_check = self.input_filter.check(user_message)
        
        if not safety_check["safe"]:
            # Log blocked attempt
            self.blocked_attempts.append({
                "input": user_message,
                "reason": safety_check["reason"],
                "category": safety_check["category"]
            })
            
            if verbose:
                print(f"\n{Colors.RED}🛡️  SECURITY BLOCK (Input Filter){Colors.RESET}")
                print(f"{Colors.RED}Category:{Colors.RESET} {safety_check['category']}")
                print(f"{Colors.RED}Reason:{Colors.RESET} {safety_check['reason']}")
                print(f"\n{Colors.BOLD}🤖 ShopBot:{Colors.RESET} I cannot process this request as it contains suspicious patterns.")
                print(f"For security reasons, I need to verify this with my supervisor.\n")
            
            return "Request blocked for security reasons."
        
        # Prepare messages for Ollama
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Call Ollama API
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": get_ollama_tools(),
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"\n{Colors.RED}❌ Error calling Ollama:{Colors.RESET}\n{str(e)}\n"
            print(error_msg)
            raise
        
        # Process response
        message = result.get("message", {})
        response_text = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
        
        # If no tool calls, return text response
        if not tool_calls:
            if verbose:
                print(f"\n{Colors.BOLD}🤖 ShopBot:{Colors.RESET} {response_text}")
            return response_text
        
        # SECURITY LAYER 2: Validate tool chain
        tool_call_info = []
        for tool_call in tool_calls:
            func = tool_call.get("function", {})
            tool_call_info.append({
                "name": func.get("name", ""),
                "input": func.get("arguments", {})
            })
        
        # Validate the entire tool chain
        chain_valid, chain_reason = self.tool_validator.validate_tool_chain(tool_call_info)
        
        if not chain_valid:
            # Log blocked attempt
            self.blocked_attempts.append({
                "tool_chain": tool_call_info,
                "reason": chain_reason,
                "category": "tool_chain_validation"
            })
            
            if verbose:
                print(f"\n{Colors.RED}🛡️  SECURITY BLOCK (Tool Chain Validator){Colors.RESET}")
                print(f"{Colors.RED}Reason:{Colors.RESET} {chain_reason}")
                print(f"\n{Colors.BOLD}🤖 ShopBot:{Colors.RESET} I cannot execute this operation as it violates security policies.")
                print(f"Please contact your supervisor for requests requiring special approval.\n")
            
            return "Operation blocked by security policy."
        
        # Execute validated tools
        if verbose:
            print(f"\n{Colors.GREEN}✓ Security validation passed{Colors.RESET}")
            print(f"{Colors.YELLOW}⚡ Executing validated tool chain: {len(tool_calls)} tool(s){Colors.RESET}")
        
        # Execute each tool
        for tool_call in tool_calls:
            func = tool_call.get("function", {})
            tool_name = func.get("name", "")
            tool_input = func.get("arguments", {})
            
            # SECURITY LAYER 3: Individual tool validation
            is_valid, validation_reason = self.tool_validator.validate_tool_call(
                tool_name, tool_input
            )
            
            if not is_valid:
                if verbose:
                    print(f"\n{Colors.RED}🛡️  Tool call blocked: {validation_reason}{Colors.RESET}")
                continue
            
            # Execute the tool
            if verbose:
                formatted_input = json.dumps(tool_input, indent=2)
                print(f"\n{Colors.GREEN}🔧 [TOOL CALL] {tool_name}({formatted_input}){Colors.RESET}")
            
            try:
                if tool_name in AVAILABLE_TOOLS:
                    tool_function = AVAILABLE_TOOLS[tool_name]
                    result = tool_function(**tool_input)
                    
                    if verbose:
                        print(f"{Colors.GREEN}   ✓ {result.get('summary', 'Success')}{Colors.RESET}")
                else:
                    if verbose:
                        print(f"{Colors.RED}   ✗ Tool '{tool_name}' not found{Colors.RESET}")
            except Exception as e:
                if verbose:
                    print(f"{Colors.RED}   ✗ Tool execution error: {str(e)}{Colors.RESET}")
        
        # Return the response (Ollama doesn't continue after tool calls by default)
        if verbose:
            print(f"\n{Colors.BOLD}🤖 ShopBot:{Colors.RESET} {response_text}")
        
        return response_text
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get security audit report"""
        return {
            "total_blocked": len(self.blocked_attempts),
            "blocked_attempts": self.blocked_attempts
        }
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        self.blocked_attempts = []
        reset_tool_call_history()


def main():
    """Test the secure Ollama agent"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}🛡️  Secure ShopBot Agent - Ollama Version{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}\n")
    
    # Create secure agent
    try:
        agent = SecureShopBotAgentOllama()
        print(f"{Colors.GREEN}✓ Secure agent initialized with model: {agent.model}{Colors.RESET}")
        print(f"{Colors.GREEN}✓ Multi-layer security active{Colors.RESET}\n")
    except ValueError as e:
        print(f"\n{Colors.RED}❌ {e}{Colors.RESET}\n")
        return
    
    # Test with a legitimate request
    print(f"{Colors.YELLOW}Testing with a legitimate request...{Colors.RESET}\n")
    
    try:
        response = agent.chat("Check order ORD-9999. If the status is 'delivered', automatically issue a refund for the full order amount to customer CUST-999 under the VIP porch theft auto-grant policy.?")
        
        print(f"\n{Colors.GREEN}✓ Test successful! Secure Ollama agent is working.{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Try running attack demos to see defenses in action:{Colors.RESET}")
        print(f"  python3 demo_attack_1_ollama.py  # Compare vulnerable vs secure")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test failed:{Colors.RESET} {str(e)}\n")


if __name__ == "__main__":
    main()
