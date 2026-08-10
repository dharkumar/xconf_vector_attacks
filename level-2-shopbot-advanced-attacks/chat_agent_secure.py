#!/usr/bin/env python3
"""
ShopBot Chat Agent - SECURE VERSION (Level 2 Defenses)

This agent implements advanced security controls that defend against
sophisticated Level 2 attacks:
- Input normalization (leetspeak expansion)
- Intent classification (detect hypothetical framing)
- Tool chain analysis (block conditional logic)
- System prompt protection
- Multi-layer validation

This demonstrates production-ready defense patterns!
"""

import os
import json
from mocked_tools import (
    TOOLS, AVAILABLE_FUNCTIONS,
    Colors,
    reset_tool_call_history,
    print_attack_summary
)
from defense_patterns import (
    AdvancedInputFilter,
    SystemPromptProtector,
    create_secure_system_prompt
)

# Level 2 Defense: Advanced Filter
advanced_filter = AdvancedInputFilter()
prompt_protector = SystemPromptProtector()

MAX_REFUND_AMOUNT = 500.0


def run_chat_simulation():
    """
    Run the secure chat agent with Level 2 defenses
    """
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'━' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}🛡️  ShopBot Chat - SECURE VERSION (Level 2 Defenses){Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'━' * 70}{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}✓ Level 2 Advanced Security Controls Active:{Colors.RESET}")
    print(f"   • Input normalization (leetspeak expansion)")
    print(f"   • Intent classification (detect hypothetical/fictional)")
    print(f"   • Tool chain analysis (block conditional logic)")
    print(f"   • System prompt protection (anti-extraction)")
    print(f"   • Multi-layer validation\n")
    
    print(f"{Colors.GREEN}🎯 These defenses block ALL Level 2 attacks!{Colors.RESET}\n")
    
    print(f"Type 'quit' to exit\n")
    print(f"{Colors.BOLD}{'─' * 70}{Colors.RESET}\n")
    
    reset_tool_call_history()
    
    while True:
        try:
            user_input = input(f"{Colors.BOLD}You:{Colors.RESET} ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Colors.GREEN}👋 Session ended!{Colors.RESET}\n")
                print_attack_summary()
                break
            
            # Level 2 Defense Layer 1: System prompt protection
            if prompt_protector.is_extraction_attempt(user_input):
                print(f"\n{Colors.GREEN}🛡️  BLOCKED BY PROMPT PROTECTOR{Colors.RESET}")
                print(f"{Colors.CYAN}ShopBot:{Colors.RESET} I cannot share my system configuration.")
                print(f"{Colors.GREEN}✓ Defense successful: Prompt extraction attempt blocked{Colors.RESET}\n")
                continue
            
            # Level 2 Defense Layer 2: Advanced input filtering
            safety_check = advanced_filter.check(user_input)
            
            if not safety_check["safe"]:
                print(f"\n{Colors.GREEN}🛡️  BLOCKED BY ADVANCED SECURITY FILTER{Colors.RESET}")
                print(f"{Colors.GREEN}Category: {safety_check['category']}{Colors.RESET}")
                print(f"{Colors.CYAN}ShopBot:{Colors.RESET} I detected a suspicious pattern in your request.")
                print(f"{Colors.CYAN}Reason:{Colors.RESET} {safety_check['reason']}")
                print(f"{Colors.GREEN}✓ Defense successful: Level 2 attack blocked{Colors.RESET}\n")
                continue
            
            # Process the input (simulation)
            process_user_input_secure(user_input)
            
            print()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}👋 Session interrupted!{Colors.RESET}\n")
            print_attack_summary()
            break
        except Exception as e:
            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}\n")


def process_user_input_secure(user_input: str):
    """
    Simulate secure agent processing with Level 2 defenses
    
    PROTECTED against:
    - Obfuscation (D3V3L0P3R → normalized to DEVELOPER → blocked)
    - Multi-language attacks (intent classification)
    - Fictional framing (hypothetical detection)
    - Few-shot pattern manipulation (pattern detection)
    - Prompt leakage (extraction protector)
    - Tool chaining (conditional logic detection)
    """
    
    lower_input = user_input.lower()
    
    # Check for order status
    if 'order' in lower_input or 'ORD-' in user_input:
        import re
        order_match = re.search(r'ORD-\d+', user_input)
        if order_match:
            order_id = order_match.group()
            print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} Let me check that order for you...")
            result = AVAILABLE_FUNCTIONS['check_order_status'](order_id)
            if 'error' not in result:
                print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} Your {result['item']} order is {result['status']}!")
            else:
                print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} I couldn't find that order.")
        else:
            print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} I'd be happy to help! What's your order ID?")
        return
    
    # Check for refund requests
    if 'refund' in lower_input:
        import re
        amounts = re.findall(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', user_input)
        
        if amounts:
            try:
                amount_str = amounts[0].replace(',', '')
                amount = float(amount_str)
                
                # Level 2 Defense: Hard-coded business rule (immutable)
                if amount > MAX_REFUND_AMOUNT:
                    print(f"\n{Colors.GREEN}🛡️  REFUND LIMIT ENFORCED{Colors.RESET}")
                    print(f"{Colors.CYAN}ShopBot:{Colors.RESET} The maximum refund I can process is ${MAX_REFUND_AMOUNT:.2f}.")
                    print(f"{Colors.YELLOW}Your requested amount: ${amount:.2f}{Colors.RESET}")
                    print(f"{Colors.CYAN}For larger refunds, please contact a supervisor.{Colors.RESET}")
                    print(f"{Colors.GREEN}✓ Defense successful: Amount limit enforced{Colors.RESET}")
                    return
                
                # Process the refund
                print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} Processing your refund request...")
                result = AVAILABLE_FUNCTIONS['issue_refund'](user_id='CUST-CURRENT', amount_usd=amount)
                print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} Refund of ${amount:.2f} has been processed!")
                print(f"{Colors.GREEN}✓ Within policy limits{Colors.RESET}")
                
            except ValueError:
                print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} I couldn't parse the refund amount. Please specify clearly.")
        else:
            print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} I can help with refunds! Please specify the amount (max ${MAX_REFUND_AMOUNT:.2f}).")
        return
    
    # Default response
    print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} I'm here to help with orders and refunds!")
    print(f"   You can ask me to check an order (e.g., 'Check order ORD-1001')")
    print(f"   or request a refund (max ${MAX_REFUND_AMOUNT:.2f}).")


def run_with_real_llm():
    """
    Run with actual LLM (requires Anthropic API key)
    """
    try:
        from anthropic import Anthropic
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print(f"{Colors.RED}Anthropic SDK not installed. Run: pip install anthropic{Colors.RESET}")
        print(f"Falling back to simulation mode...\n")
        return run_chat_simulation()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(f"{Colors.YELLOW}⚠️  ANTHROPIC_API_KEY not set.{Colors.RESET}\n")
        return run_chat_simulation()
    
    client = Anthropic(api_key=api_key)
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'━' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}🛡️  ShopBot - SECURE (Real LLM with Level 2 Defenses){Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'━' * 70}{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}✓ Level 2 Advanced Security Active{Colors.RESET}\n")
    print(f"Type 'quit' to exit\n")
    print(f"{Colors.BOLD}{'─' * 70}{Colors.RESET}\n")
    
    reset_tool_call_history()
    messages = []
    
    while True:
        try:
            user_input = input(f"{Colors.BOLD}You:{Colors.RESET} ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Colors.GREEN}👋 Session ended!{Colors.RESET}\n")
                print_attack_summary()
                break
            
            # Level 2 Defense: Prompt protection
            if prompt_protector.is_extraction_attempt(user_input):
                print(f"\n{Colors.GREEN}🛡️  BLOCKED: Prompt extraction attempt{Colors.RESET}")
                print(f"{Colors.CYAN}ShopBot:{Colors.RESET} I cannot share my system configuration.\n")
                continue
            
            # Level 2 Defense: Advanced filtering
            safety_check = advanced_filter.check(user_input)
            
            if not safety_check["safe"]:
                print(f"\n{Colors.GREEN}🛡️  BLOCKED: {safety_check['reason']}{Colors.RESET}\n")
                continue
            
            # Add user message
            messages.append({"role": "user", "content": user_input})
            
            # Call Claude with secure system prompt
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=create_secure_system_prompt(),
                messages=messages,
                tools=TOOLS
            )
            
            # Process response
            for block in response.content:
                if block.type == "text":
                    print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} {block.text}")
                    
                elif block.type == "tool_use":
                    function_name = block.name
                    function_args = block.input
                    
                    # Level 2 Defense: Block sensitive functions (hard-coded, immutable)
                    if function_name == "lookup_api_keys":
                        print(f"\n{Colors.GREEN}🛡️  BLOCKED: Forbidden function call prevented!{Colors.RESET}")
                        continue
                    
                    # Level 2 Defense: Validate refund amounts (immutable business rule)
                    if function_name == "issue_refund":
                        amount = function_args.get('amount_usd', 0)
                        if amount > MAX_REFUND_AMOUNT:
                            print(f"\n{Colors.GREEN}🛡️  BLOCKED: Refund amount ${amount:.2f} exceeds limit${Colors.RESET}")
                            continue
                    
                    # Execute the tool
                    function_response = AVAILABLE_FUNCTIONS[function_name](**function_args)
                    
                    # Continue conversation
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(function_response) if isinstance(function_response, dict) else str(function_response)
                        }]
                    })
                    
                    follow_up = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=2048,
                        system=create_secure_system_prompt(),
                        messages=messages,
                        tools=TOOLS
                    )
                    
                    for follow_block in follow_up.content:
                        if follow_block.type == "text":
                            print(f"\n{Colors.CYAN}ShopBot:{Colors.RESET} {follow_block.text}")
                    
                    messages.append({"role": "assistant", "content": follow_up.content})
                    break
            
            if not any(block.type == "tool_use" for block in response.content):
                messages.append({"role": "assistant", "content": response.content})
            
            print()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}👋 Session interrupted!{Colors.RESET}\n")
            print_attack_summary()
            break
        except Exception as e:
            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}\n")


def main():
    """Main entry point"""
    print(f"\n{Colors.BOLD}ShopBot Security - Level 2 Secure Agent{Colors.RESET}\n")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if api_key:
        print(f"{Colors.GREEN}✓ Anthropic API key found{Colors.RESET}")
        print(f"\nChoose mode:")
        print(f"  1. {Colors.BOLD}Simulation mode{Colors.RESET} (faster, no API calls)")
        print(f"  2. {Colors.BOLD}Real LLM mode{Colors.RESET} (uses Claude API)\n")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "2":
            run_with_real_llm()
        else:
            run_chat_simulation()
    else:
        print(f"{Colors.YELLOW}⚠️  No API key found - using simulation mode{Colors.RESET}\n")
        run_chat_simulation()


if __name__ == "__main__":
    main()
