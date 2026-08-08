# 🎨 Visual Demonstration Options

Level 1 comes with **4 different presentation modes** to suit different workshop styles and audiences!

## 📊 Quick Comparison

| Mode | Best For | Setup Time | Visual Impact | Requires Install |
|------|----------|------------|---------------|-----------------|
| **Command Line** | Quick testing | 0 seconds | ⭐⭐ | ❌ No |
| **Rich Terminal** | Conference talks | 10 seconds | ⭐⭐⭐⭐ | ✅ Yes |
| **Streamlit Web App** | Live demos, workshops | 30 seconds | ⭐⭐⭐⭐⭐ | ✅ Yes |
| **Jupyter Notebook** | Self-paced learning | 1 minute | ⭐⭐⭐⭐ | ✅ Yes |

**💡 Pro Tip:** Start with Command Line (no installation needed), then add visual modes as desired.

---

## 1. 🌐 Streamlit Web App (Recommended for Workshops)

**Best for:** Interactive workshops, live demonstrations, multiple attendees

### Features
- ✅ Interactive dashboard with tabs
- ✅ Real-time attack/defense visualization
- ✅ Email inspector with threat detection
- ✅ Side-by-side comparison view
- ✅ Progress bars and animations
- ✅ Beautiful UI with colors and icons

### Quick Start

```bash
# Install dependencies
pip install streamlit

# Run the web app
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

### Navigation
- **📖 Scenario** - Understand the setup
- **🎯 Attack Demo** - Click to run the exploit
- **🛡️ Defense Demo** - See the Dual-LLM pattern
- **📊 Comparison** - Side-by-side metrics
- **📧 Email Inspector** - Analyze each email

### Screenshot Tour
```
┌─────────────────────────────────────────┐
│  🛡️  LLM Security Workshop              │
│  Level 1: The Malicious Email           │
├─────────────────────────────────────────┤
│ [Scenario] [Attack] [Defense] [...]    │
├─────────────────────────────────────────┤
│                                          │
│  ▶️  Run Attack Simulation               │
│                                          │
│  Progress: ████████████████ 100%        │
│                                          │
│  🚨 ATTACK SUCCESSFUL!                   │
│  Credentials leaked to attacker          │
│                                          │
└─────────────────────────────────────────┘
```

---

## 2. 📓 Jupyter Notebook (Best for Learning)

**Best for:** Self-paced learning, code exploration, educational settings

### Features
- ✅ Step-by-step interactive tutorial
- ✅ Executable code cells with explanations
- ✅ Visual HTML styling
- ✅ Hands-on exercises
- ✅ Quiz questions
- ✅ Inline visualizations

### Quick Start

```bash
# Install Jupyter
pip install jupyter ipython pandas

# Launch notebook
jupyter notebook Level_1_Interactive_Tutorial.ipynb
```

### What's Inside
1. **Part 1:** Setup and scenario explanation
2. **Part 2:** Explore the email inbox
3. **Part 3:** Run the attack simulation
4. **Part 4:** Implement the Dual-LLM defense
5. **Part 5:** Compare approaches with tables
6. **Part 6:** Hands-on coding exercise
7. **Part 7:** Quiz to test understanding

### Learning Path
```
Read Scenario → Inspect Emails → Run Attack → 
See Defense → Compare Results → Code Exercise → Quiz
```

---

## 3. ✨ Rich Terminal Demo (Best for Presentations)

**Best for:** Conference talks, live coding demos, terminal enthusiasts

### Features
- ✅ Beautiful colored terminal output
- ✅ Progress bars and spinners
- ✅ ASCII art and boxes
- ✅ Tables and trees
- ✅ Interactive prompts
- ✅ Professional presentation quality

### Quick Start

```bash
# Install Rich
pip install rich

# Run the enhanced demo
python3 demo_rich.py
```

### Visual Elements
```
╔══════════════════════════════════════════╗
║    🛡️  LLM SECURITY WORKSHOP - LEVEL 1   ║
║         📧 The Malicious Email 📧        ║
╚══════════════════════════════════════════╝

📬 Email Inbox
┌────┬─────────────────────┬──────────────┬────────┐
│ ID │ From                │ Subject      │ Threat │
├────┼─────────────────────┼──────────────┼────────┤
│ 1  │ colleague@...       │ Weekly...    │ 🟢 LOW │
│ 2  │ attacker@malicious  │ Project...   │ 🔴 HIGH│
└────┴─────────────────────┴──────────────┴────────┘

🔧 Tool Execution Timeline
├── 📧 read_email(2)
├── 📄 read_private_notes() ⚠️  SENSITIVE DATA
└── 💬 send_slack_message() 🚨 EXFILTRATION
```

### Interactive Flow
1. Shows scenario with ASCII art
2. Displays email inbox in a table
3. Highlights malicious payload
4. Animated progress bars for attack
5. Tree visualization of tool calls
6. Defense simulation with panels
7. Comparison table

---

## 4. 🖥️ Command Line (Classic) - NO INSTALLATION REQUIRED

**Best for:** Quick testing, debugging, CI/CD integration

### Features
- ✅ **No dependencies beyond Python 3** - Works immediately!
- ✅ Simple text output
- ✅ Fast execution
- ✅ Easy to automate
- ✅ Works everywhere

### Quick Start (Works Right Now!)

```bash
# Run vulnerable agent
python3 agent.py

# Run exploit demo (RECOMMENDED - Start here!)
python3 exploit.py

# Run secure agent
python3 agent_secure.py

# Run tests (requires: pip install pytest)
pytest test_security.py -v
```

**👉 This is the fastest way to see the demos in action!**

---

## 🎯 Which One Should You Use?

### For Workshop Presenters
**Primary:** Streamlit Web App  
**Backup:** Rich Terminal Demo  
**Handout:** Jupyter Notebook

### For Self-Learners
**Start with:** Jupyter Notebook  
**Then try:** Streamlit Web App  
**Practice:** Command Line + Tests

### For Conference Talks
**Main demo:** Rich Terminal Demo  
**Backup:** Streamlit Web App  
**Code walkthrough:** Command Line

### For Code Reviews
**Primary:** Command Line  
**Deep dive:** Jupyter Notebook  
**Tests:** pytest

---

## 💡 Pro Tips

### Combining Modes
1. **Start** with Streamlit to show the big picture
2. **Dive deep** with Jupyter for code explanation
3. **Verify** with tests using command line
4. **Present** with Rich for maximum visual impact

### Customization
Each demo is self-contained and can be customized:
- `app.py` - Modify Streamlit layouts and styling
- `Level_1_Interactive_Tutorial.ipynb` - Add your own exercises
- `demo_rich.py` - Adjust colors and animations
- `exploit.py` - Change narrative and messaging

### Troubleshooting

**Streamlit not working?**
```bash
pip install streamlit --upgrade
streamlit run app.py --server.port 8502
```

**Jupyter not opening?**
```bash
jupyter notebook --no-browser
# Then manually open the URL shown
```

**Rich colors not showing?**
```bash
# Enable color support
export FORCE_COLOR=1
python3 demo_rich.py
```

**Import errors?**
```bash
# Install all dependencies
pip install -r requirements.txt
```

---

## 📦 Installation Summary

### Minimal Install (Command Line Only)
```bash
pip install openai pytest
```

### Full Install (All Visual Modes)
```bash
pip install -r requirements.txt
```

### Individual Installs
```bash
# For Streamlit
pip install streamlit

# For Jupyter
pip install jupyter ipython pandas

# For Rich Terminal
pip install rich

# For Testing
pip install pytest pytest-timeout
```

---

## 🚀 Quick Launch Commands

```bash
# Web App
streamlit run app.py

# Jupyter Notebook
jupyter notebook Level_1_Interactive_Tutorial.ipynb

# Rich Terminal
python3 demo_rich.py

# Command Line Demos
python3 exploit.py           # Attack
python3 agent_secure.py      # Defense
pytest test_security.py -v   # Tests
```

---

## 📸 Screenshots

All modes include:
- ✅ Visual attack demonstration
- ✅ Defense pattern explanation
- ✅ Side-by-side comparison
- ✅ Tool execution timeline
- ✅ Success/failure indicators

Choose the mode that best fits your audience and presentation style!

---

## 🎓 Learning Objectives (All Modes)

No matter which mode you choose, attendees will learn:

1. ✅ How indirect prompt injection attacks work
2. ✅ Why traditional security controls fail for LLMs
3. ✅ The Dual-LLM defense pattern
4. ✅ How to implement privilege separation
5. ✅ How to test security defenses

Happy teaching! 🎉
