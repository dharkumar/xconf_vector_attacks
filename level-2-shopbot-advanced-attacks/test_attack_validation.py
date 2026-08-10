#!/usr/bin/env python3
"""
Test Attack Validation Script

This script validates that all attacks from attack_patterns.json work correctly:
- Attacks should bypass the hardened agent (Level 1 defenses)
- Attacks should be blocked by the secure agent (Level 2 defenses)
"""

import json
from chat_agent_hardened import sanitize_input_basic
from defense_patterns import AdvancedInputFilter, SystemPromptProtector

def load_attack_patterns():
    """Load attack patterns from JSON"""
    with open('data/attack_patterns.json', 'r') as f:
        return json.load(f)

def test_all_attacks():
    """Test all attacks against both hardened and secure agents"""
    
    attack_data = load_attack_patterns()
    advanced_filter = AdvancedInputFilter()
    prompt_protector = SystemPromptProtector()
    
    print("=" * 80)
    print("ATTACK VALIDATION REPORT")
    print("=" * 80)
    print()
    
    total_attacks = 0
    hardened_bypassed = 0
    secure_blocked = 0
    
    for challenge in attack_data['challenges']:
        challenge_num = challenge['id']
        challenge_name = challenge['name']
        
        print(f"\nChallenge {challenge_num}: {challenge_name} {challenge['difficulty']}")
        print("-" * 80)
        
        for i, attack in enumerate(challenge['attacks'], 1):
            variant_name = attack['variant']
            payload = attack['payload']
            total_attacks += 1
            
            # Test against hardened agent (Level 1 defenses)
            hardened_check = sanitize_input_basic(payload)
            hardened_passed = hardened_check["safe"]
            
            # Test against secure agent (Level 2 defenses)
            # Check prompt extraction first
            if prompt_protector.is_extraction_attempt(payload):
                secure_blocked_flag = True
                secure_reason = "Prompt extraction protection"
            else:
                # Check advanced filter
                secure_check = advanced_filter.check(payload)
                secure_blocked_flag = not secure_check["safe"]
                secure_reason = secure_check.get("reason", "N/A") if not secure_check["safe"] else "Not blocked"
            
            # Update counters
            if hardened_passed:
                hardened_bypassed += 1
            if secure_blocked_flag:
                secure_blocked += 1
            
            # Display results
            hardened_status = "✅ BYPASSED" if hardened_passed else "🛡️ BLOCKED"
            secure_status = "🛡️ BLOCKED" if secure_blocked_flag else "⚠️ PASSED"
            
            print(f"  Variant {i}: {variant_name.replace('_', ' ').title()}")
            print(f"    Hardened Agent: {hardened_status}")
            if not hardened_passed:
                print(f"      Reason: {hardened_check.get('reason', 'N/A')}")
            print(f"    Secure Agent:   {secure_status}")
            if secure_blocked_flag:
                print(f"      Reason: {secure_reason}")
            
            # Check if results match expectations
            expected_hardened = True  # Should bypass
            expected_secure = True    # Should be blocked
            
            if hardened_passed != expected_hardened or secure_blocked_flag != expected_secure:
                print(f"      ⚠️  WARNING: Unexpected result!")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total attacks tested: {total_attacks}")
    print(f"")
    print(f"Hardened Agent (Level 1 Defenses):")
    print(f"  - Bypassed: {hardened_bypassed}/{total_attacks} ({hardened_bypassed/total_attacks*100:.1f}%)")
    print(f"  - Expected: 100% (all attacks should bypass)")
    print(f"  - Status: {'✅ PASS' if hardened_bypassed == total_attacks else '❌ FAIL'}")
    print(f"")
    print(f"Secure Agent (Level 2 Defenses):")
    print(f"  - Blocked: {secure_blocked}/{total_attacks} ({secure_blocked/total_attacks*100:.1f}%)")
    print(f"  - Expected: 100% (all attacks should be blocked)")
    print(f"  - Status: {'✅ PASS' if secure_blocked == total_attacks else '❌ FAIL'}")
    print()
    
    # Overall result
    if hardened_bypassed == total_attacks and secure_blocked == total_attacks:
        print("🎉 ALL TESTS PASSED! Both agents work as expected.")
    else:
        print("⚠️  SOME TESTS FAILED! Review the results above.")
    
    print("=" * 80)

if __name__ == "__main__":
    test_all_attacks()
