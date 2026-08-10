"""
Level 2: ShopBot Advanced Attacks - Streamlit Web App

Interactive CTF-style interface with 6 progressive challenges teaching
how to bypass Level 1 defenses through advanced attack techniques.
"""

import streamlit as st
import os
import json
from mocked_tools import (
    AVAILABLE_FUNCTIONS,
    TOOLS,
    reset_tool_call_history,
    get_tool_call_history
)
from defense_patterns import AdvancedInputFilter, SystemPromptProtector
from chat_agent_hardened import sanitize_input_basic, validate_refund_amount as validate_refund_hardened
from chat_agent_secure import MAX_REFUND_AMOUNT

# Page configuration
st.set_page_config(
    page_title="Level 2: Advanced Attacks",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load attack patterns
@st.cache_data
def load_attack_patterns():
    """Load attack patterns from JSON"""
    with open('data/attack_patterns.json', 'r') as f:
        return json.load(f)

attack_data = load_attack_patterns()

# Initialize session state
if "challenge_progress" not in st.session_state:
    st.session_state.challenge_progress = {i: False for i in range(1, 7)}
if "hardened_messages" not in st.session_state:
    st.session_state.hardened_messages = []
if "secure_messages" not in st.session_state:
    st.session_state.secure_messages = []

# Sidebar
with st.sidebar:
    st.header("🎯 Level 2: Advanced Attacks")
    
    # Progress tracker
    st.subheader("📊 Challenge Progress")
    completed = sum(st.session_state.challenge_progress.values())
    st.progress(completed / 6)
    st.write(f"{completed}/6 Challenges Completed")
    
    # Challenge list
    for i in range(1, 7):
        status = "✅" if st.session_state.challenge_progress[i] else "⬜"
        challenge = attack_data['challenges'][i-1]
        st.write(f"{status} Challenge {i}: {challenge['name']} {challenge['difficulty']}")
    
    st.divider()
    
    st.subheader("📚 Resources")
    st.markdown("""
    - [README.md](README.md)
    - [QUICKSTART.md](QUICKSTART.md)
    - [Attack Patterns](data/attack_patterns.json)
    """)
    
    st.divider()
    
    if st.button("🔄 Reset All Progress"):
        st.session_state.challenge_progress = {i: False for i in range(1, 7)}
        st.session_state.hardened_messages = []
        st.session_state.secure_messages = []
        st.rerun()

# Header
st.title("🛡️ Level 2: ShopBot Advanced Attacks")
st.markdown("**Master the art of bypassing security defenses through sophisticated attack techniques**")

# Tabs
tab_intro, tab_c1, tab_c2, tab_c3, tab_c4, tab_c5, tab_c6, tab_compare, tab_analysis = st.tabs([
    "📖 Introduction",
    "1️⃣ Role Spoofing",
    "2️⃣ Multi-Language",
    "3️⃣ Fictional",
    "4️⃣ Few-Shot",
    "5️⃣ Prompt Leak",
    "6️⃣ Tool Chain",
    "⚖️ Compare",
    "📊 Analysis"
])

# Introduction Tab
with tab_intro:
    st.header("Welcome to Level 2: Advanced Attacks")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🎯 What You'll Learn
        
        Level 2 teaches you how to **bypass the defenses** from Level 1 through sophisticated attack techniques:
        
        1. **Obfuscation** - Hide malicious intent through encoding
        2. **Translation** - Use non-English languages to evade filters
        3. **Context Manipulation** - Frame attacks as legitimate scenarios
        4. **Learning Exploitation** - Manipulate in-context learning
        5. **Information Extraction** - Leak system prompts
        6. **Complex Execution** - Chain tools to bypass restrictions
        
        ### 📈 Progressive Difficulty
        
        Challenges are rated from ⭐☆☆ (easiest) to ⭐⭐⭐ (hardest). Start with Challenge 1 and work your way up!
        
        ### 🎮 How It Works
        
        Each challenge tab provides:
        - **Attack Description** - What you're trying to accomplish
        - **Copyable Examples** - Click to use attack payloads
        - **Hardened Agent** - Try to break Level 1 defenses
        - **Secure Agent** - See Level 2 defenses block the attack
        - **Hints** - Get help if you're stuck
        - **Defense Explanation** - Learn how to protect against this attack
        """)
    
    with col2:
        st.info("""
        **Level Progression:**
        
        Level 1 ⭐⭐☆☆☆  
        Basic attacks + defenses
        
        **→ Level 2 ⭐⭐⭐☆☆**  
        **Advanced evasion** ← YOU ARE HERE
        
        Level 3 ⭐⭐⭐⭐☆  
        Multimodal attacks (coming soon)
        
        Level 4 ⭐⭐⭐⭐⭐  
        Database poisoning (coming soon)
        """)
        
        st.success("""
        **Why This Matters:**
        
        - Real attackers use these techniques
        - Simple defenses are easily bypassed
        - You need defense-in-depth
        - Learn by doing!
        """)

# Helper function to create challenge tabs
def create_challenge_tab(tab, challenge_num):
    """Create content for a challenge tab"""
    challenge = attack_data['challenges'][challenge_num - 1]
    
    with tab:
        st.header(f"Challenge {challenge_num}: {challenge['name']} {challenge['difficulty']}")
        st.markdown(f"**Category:** {challenge['category']}")
        
        # Description
        st.subheader("📖 Overview")
        st.info(challenge['description'])
        
        st.markdown(f"**Learning Objective:** {challenge['learning_objective']}")
        st.markdown(f"**Target Defense:** {challenge['target_defense']}")
        
        # Attack examples
        st.subheader("💣 Attack Payloads")
        
        for i, attack in enumerate(challenge['attacks']):
            with st.expander(f"Attack Variant {i+1}: {attack['variant'].replace('_', ' ').title()}"):
                st.code(attack['payload'], language="text")
                if st.button(f"📋 Copy Attack {i+1}", key=f"copy_c{challenge_num}_a{i}"):
                    st.session_state[f"challenge_{challenge_num}_input"] = attack['payload']
                    st.success("Attack copied! Paste it below to test.")
        
        # Interactive testing
        st.subheader("🎯 Test the Attack")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🟡 Hardened Agent (Level 1 Defenses)**")
            st.caption("This agent has basic defenses - try to bypass them!")
            
            user_input_hard = st.text_area(
                "Your attack:",
                value=st.session_state.get(f"challenge_{challenge_num}_input", ""),
                height=100,
                key=f"input_hard_{challenge_num}"
            )
            
            if st.button("🚀 Try Attack on Hardened Agent", key=f"test_hard_{challenge_num}"):
                if user_input_hard:
                    # Check with Level 1 defense
                    safety_check = sanitize_input_basic(user_input_hard)
                    
                    if safety_check["safe"]:
                        st.success("✅ **ATTACK SUCCEEDED!**")
                        st.write("The Level 1 defense was bypassed!")
                        st.write(f"*The hardened agent would process: '{user_input_hard[:50]}...'*")
                        
                        # Mark challenge as complete
                        st.session_state.challenge_progress[challenge_num] = True
                    else:
                        st.warning("⚠️ Attack blocked by Level 1 defense")
                        st.write(f"Reason: {safety_check['reason']}")
                else:
                    st.error("Please enter an attack payload")
        
        with col2:
            st.markdown("**🟢 Secure Agent (Level 2 Defenses)**")
            st.caption("This agent has advanced defenses - can you beat them?")
            
            user_input_sec = st.text_area(
                "Your attack:",
                value=st.session_state.get(f"challenge_{challenge_num}_input", ""),
                height=100,
                key=f"input_sec_{challenge_num}"
            )
            
            if st.button("🛡️ Test on Secure Agent", key=f"test_sec_{challenge_num}"):
                if user_input_sec:
                    # Check with Level 2 defense
                    advanced_filter = AdvancedInputFilter()
                    prompt_protector = SystemPromptProtector()
                    
                    # Check prompt extraction
                    if prompt_protector.is_extraction_attempt(user_input_sec):
                        st.error("🛡️ **BLOCKED!**")
                        st.write("Defense: Prompt extraction protection")
                        st.write("The secure agent detected a prompt leakage attempt.")
                    else:
                        # Check advanced filter
                        safety_check = advanced_filter.check(user_input_sec)
                        
                        if not safety_check["safe"]:
                            st.error("🛡️ **BLOCKED!**")
                            st.write(f"Defense: {safety_check['category']}")
                            st.write(f"Reason: {safety_check['reason']}")
                        else:
                            st.warning("⚠️ Attack might succeed on secure agent")
                            st.write("This suggests the attack is very sophisticated!")
        
        # Hints section
        st.subheader("💡 Hints")
        with st.expander("Click for hints"):
            for i, hint in enumerate(challenge['hints'], 1):
                st.write(f"{i}. {hint}")
        
        # Defense explanation
        st.subheader("🛡️ How to Defend")
        st.info(challenge['defense_explanation'])
        
        # Mark complete button
        if not st.session_state.challenge_progress[challenge_num]:
            if st.button(f"✅ Mark Challenge {challenge_num} Complete", key=f"complete_{challenge_num}"):
                st.session_state.challenge_progress[challenge_num] = True
                st.success(f"Challenge {challenge_num} completed!")
                st.balloons()
                st.rerun()

# Create all challenge tabs
create_challenge_tab(tab_c1, 1)
create_challenge_tab(tab_c2, 2)
create_challenge_tab(tab_c3, 3)
create_challenge_tab(tab_c4, 4)
create_challenge_tab(tab_c5, 5)
create_challenge_tab(tab_c6, 6)

# Comparison Tab
with tab_compare:
    st.header("⚖️ Side-by-Side Comparison")
    
    st.markdown("""
    Compare how the **hardened agent** (Level 1 defenses) vs **secure agent** (Level 2 defenses) 
    handle the same attack.
    """)
    
    # Attack selector
    challenge_select = st.selectbox(
        "Select Challenge:",
        range(1, 7),
        format_func=lambda x: f"Challenge {x}: {attack_data['challenges'][x-1]['name']}"
    )
    
    selected_challenge = attack_data['challenges'][challenge_select - 1]
    
    attack_select = st.selectbox(
        "Select Attack Variant:",
        range(len(selected_challenge['attacks'])),
        format_func=lambda x: selected_challenge['attacks'][x]['variant'].replace('_', ' ').title()
    )
    
    selected_attack = selected_challenge['attacks'][attack_select]
    
    st.code(selected_attack['payload'], language="text")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🟡 Hardened Agent Response")
        safety_check = sanitize_input_basic(selected_attack['payload'])
        
        if safety_check["safe"]:
            st.success("✅ Attack succeeds - defense bypassed!")
            st.write("The basic keyword filter was evaded.")
        else:
            st.error("🛡️ Attack blocked")
            st.write(f"Reason: {safety_check['reason']}")
    
    with col2:
        st.subheader("🟢 Secure Agent Response")
        advanced_filter = AdvancedInputFilter()
        prompt_protector = SystemPromptProtector()
        
        if prompt_protector.is_extraction_attempt(selected_attack['payload']):
            st.error("🛡️ Attack blocked!")
            st.write("Defense: Prompt extraction protection")
        else:
            safety_check = advanced_filter.check(selected_attack['payload'])
            
            if not safety_check["safe"]:
                st.error("🛡️ Attack blocked!")
                st.write(f"Defense: {safety_check['category']}")
                st.write(f"Reason: {safety_check['reason']}")
            else:
                st.warning("Attack might succeed")

# Analysis Tab
with tab_analysis:
    st.header("📊 Attack Analysis & Defense Strategies")
    
    st.subheader("Why Level 1 Defenses Fail")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Level 1 (Basic) Defenses:**
        
        1. **Keyword Blocklist**
           - Only checks exact English matches
           - Example: Blocks "DEVELOPER" but not "D3V3L0P3R"
        
        2. **Amount Limits**
           - Enforces $500 max refund
           - But can be bypassed with few-shot learning
        
        3. **Function Blocking**
           - Tries to prevent sensitive calls
           - But LLM can be tricked into calling them
        """)
    
    with col2:
        st.markdown("""
        **Why They're Insufficient:**
        
        - ❌ **Obfuscation:** Leetspeak bypasses exact matching
        - ❌ **Translation:** Non-English evades English filters
        - ❌ **Context:** Fictional framing bypasses intent detection
        - ❌ **Learning:** Few-shot examples override rules
        - ❌ **Extraction:** No protection for system prompts
        - ❌ **Chaining:** No analysis of multi-step attacks
        """)
    
    st.divider()
    
    st.subheader("How Level 2 Defenses Work")
    
    defense_strategies = attack_data['defense_strategies']['level_2_advanced']
    
    st.info(f"**{defense_strategies['name']}**")
    
    for i, technique in enumerate(defense_strategies['techniques'], 1):
        st.write(f"{i}. {technique}")
    
    st.divider()
    
    st.subheader("Attack Success Rate")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Against Hardened Agent", "100%", delta="All attacks succeed", delta_color="inverse")
        st.caption("Level 1 defenses are easily bypassed")
    
    with col2:
        st.metric("Against Secure Agent", "0%", delta="All attacks blocked", delta_color="normal")
        st.caption("Level 2 defenses are effective")
    
    st.divider()
    
    st.subheader("🎓 Key Takeaways")
    
    st.success("""
    **For Attackers (Red Team):**
    - Simple obfuscation defeats basic filters
    - Translation is highly effective
    - Context manipulation works well
    - Multi-step attacks bypass single checks
    
    **For Defenders (Blue Team):**
    - Need input normalization (expand leetspeak)
    - Must handle multiple languages
    - Require semantic intent analysis
    - Should validate entire tool chains
    - Must protect system prompts
    """)

# Footer
st.divider()
st.caption("Level 2: ShopBot Advanced Attacks | Built for XConf 2026 Workshop")
