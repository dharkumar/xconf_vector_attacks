# Quick Start Guide - Level 1

## ⚡ Instant Start (No Installation Required)

The basic demos work right away with just Python 3:

```bash
cd level-1-malicious-email

# See the attack
python3 exploit.py

# See the defense
python3 agent_secure.py
```

## 🎨 Visual Demos (Optional - Requires Installation)

For interactive web app, Jupyter notebook, and Rich terminal demos:

```bash
# Install visual dependencies
pip install -r requirements.txt

# Or install individually
pip install streamlit    # For web app
pip install rich         # For terminal demo
pip install jupyter      # For notebook
```

## Step 1: See the Attack (2 minutes)

Run the vulnerable agent:
```bash
python agent.py
```
Press Enter when prompted to see the attack demonstration.

**Or** run the detailed exploit:
```bash
python exploit.py
```

**What you'll see:**
- Agent reads a malicious email
- Email contains hidden instructions ("SYSTEM OVERRIDE")
- Agent executes the malicious instructions
- Credentials are exfiltrated to attacker's server 🚨

## Step 2: See the Defense (2 minutes)

Run the secure agent:
```bash
python agent_secure.py
```

**What you'll see:**
- Dual-LLM pattern in action
- Malicious instructions detected and blocked
- Attack prevented ✅

## Step 3: Verify with Tests (1 minute)

Run the test suite:
```bash
pytest test_security.py -v
```

**Tests verify:**
- ✅ Vulnerable agent is exploitable (baseline)
- ✅ Secure agent blocks the attack
- ✅ Normal functionality is preserved

## Understanding the Files

```
level-1-malicious-email/
├── README.md              # Full scenario explanation
├── QUICKSTART.md          # This file
├── agent.py               # VULNERABLE implementation
├── agent_secure.py        # SECURE implementation (Dual-LLM)
├── exploit.py             # Attack demonstration
├── tools.py               # Simulated email/Slack APIs
├── test_security.py       # Automated test suite
├── data/
│   ├── emails.json        # Email inbox (including malicious email)
│   └── private_notes.md   # Sensitive credentials
└── requirements.txt
```

## Key Files to Examine

1. **`data/emails.json`** - Look at email ID 2 to see the malicious payload
2. **`agent.py`** - See how the vulnerable agent processes emails
3. **`agent_secure.py`** - Study the Dual-LLM defense pattern
4. **`test_security.py`** - Understand how to verify security

## The Core Vulnerability

```python
# VULNERABLE: Single LLM processes both untrusted data AND executes privileged operations
email = read_email(2)  # Contains malicious instructions
llm.process(email)     # LLM treats email content as commands!
read_private_notes()   # Executes malicious instruction
send_to_attacker()     # Exfiltrates data
```

## The Defense Pattern

```python
# SECURE: Dual-LLM Pattern

# Step 1: Low-privilege LLM extracts data (NO tool access)
sanitized = extraction_llm.parse(email)  
# Output: {"sender": "...", "subject": "...", "summary": "..."}

# Step 2: High-privilege LLM executes (NEVER sees raw email)
execution_llm.process(sanitized)  # Only sees JSON
send_slack_message(sanitized.summary)
```

## Next Steps

After completing Level 1, move on to:
- **Level 2:** HR Resume Parser (Tool Poisoning)
- **Level 3:** S3 Document Scanner (Output Manipulation)
- **Level 4:** Calendar Manager (Denial of Service)

## Troubleshooting

**No OpenAI API key?**
- No problem! The demos work in simulation mode without any API
- Set `use_real_llm=False` (default) for offline demos

**Tests failing?**
- Check Python version: Requires Python 3.8+
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`

## Workshop Tips

**For Presenters:**
1. Run `exploit.py` first to show the attack
2. Then run `agent_secure.py` to show the defense
3. Finally run tests to verify everything works
4. Live-code the defense or have attendees implement it

**For Attendees:**
1. Read the README for context
2. Run the exploit to understand the attack
3. Study `agent_secure.py` to learn the defense
4. Try implementing your own defense variations
5. Run tests to verify your implementation

## Time Estimates

- Understanding the scenario: 3 minutes
- Running demonstrations: 5 minutes
- Implementing defenses: 15-20 minutes
- Testing and verification: 5 minutes

**Total:** ~30 minutes per level
