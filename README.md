# AI-Age Attack Vectors: Securing LLM-Powered Agentic Applications

**A Hands-On CTF-Style Workshop on LLM Security**

---

## 🎯 Workshop Overview

This workshop teaches developers and security engineers how to **secure LLM-powered agentic applications** against real-world attacks. Through hands-on CTF challenges, you'll learn to identify vulnerabilities and implement production-ready defenses.

### Why This Matters

Organizations are rapidly deploying LLM agents with access to:
- Internal tools and databases
- Privileged APIs
- Sensitive credentials
- Autonomous decision-making capabilities

**Traditional security controls fail** because LLMs interpret natural language as instructions. This workshop provides immediately actionable defenses for real threats.

---

## 🎓 Learning Objectives

By the end of this workshop, attendees will:

1. ✅ Understand how indirect prompt injection attacks work
2. ✅ Recognize why traditional security patterns fail for LLMs
3. ✅ Implement the Dual-LLM defense pattern
4. ✅ Apply privilege separation and egress filtering
5. ✅ Test security defenses with automated verification

---

## 🏆 Workshop Levels

### ✅ Level 1: The Malicious Email (FULLY VALIDATED)

**Attack:** Indirect Prompt Injection + Data Exfiltration  
**Scenario:** Executive Assistant AI processes corporate emails  
**Defense:** Dual-LLM Pattern with privilege separation

**Status:** 🟢 **Fully Validated & Production Ready**  
**Test Coverage:** ✅ 9/9 security tests passing (100%)  
**Security Score:** 🛡️ Attack blocked with all defenses active  
**Location:** [`level-1-malicious-email/`](level-1-malicious-email/)

**Quick Start:**
```bash
cd level-1-malicious-email

# See the attack
python3 exploit.py

# See the defense
python3 agent_secure.py

# Run complete demo (attack + defense + comparison)
python3 demo_complete.py

# Run automated tests
pytest test_security.py -v
```

**Features:**
- ✅ **5 presentation modes** (CLI, Complete Demo, Web App, Jupyter, Rich Terminal)
- ✅ **Streamlit web app** with 5 interactive tabs and visual metrics
- ✅ **Jupyter notebook** with step-by-step tutorial (20-25 min)
- ✅ **Complete validation report** documenting all security controls
- ✅ **9 automated security tests** with 100% pass rate
- ✅ **Real-time LLM demonstrations** with Claude (Anthropic) support

**Validation Results:**
- 🛡️ Vulnerable agent confirmed exploitable (baseline established)
- 🛡️ Secure agent blocks 100% of attacks (zero data exfiltration)
- 🛡️ All 4 defense layers validated (input sanitization, egress filtering, dual-LLM, least privilege)
- 🛡️ Legitimate functionality preserved (normal emails processed correctly)

[→ View Level 1 Details](level-1-malicious-email/README.md) | [📄 View Validation Report](level-1-malicious-email/VALIDATION_REPORT.md)

---

### 🚧 Level 2: The Poisoned Resume (Planned)

**Attack:** Tool Poisoning + Over-Permission  
**Scenario:** HR agent parsing PDF resumes  
**Defense:** Least privilege + Schema validation (Pydantic)

**Status:** 🔴 Not yet implemented

---

### 🚧 Level 3: The S3 Exfiltration (Planned)

**Attack:** Output Manipulation + Tracker Pixel  
**Scenario:** Document scanner generating markdown reports  
**Defense:** Output sanitization pipelines

**Status:** 🔴 Not yet implemented

---

### 🚧 Level 4: The Chaos Calendar Loop (Planned)

**Attack:** Denial of Service + Wallet Exhaustion  
**Scenario:** Calendar automation agent  
**Defense:** Stateful middleware + Circuit breakers

**Status:** 🔴 Not yet implemented

---

## 🚀 Getting Started

### Prerequisites

**Technical Requirements:**
- Python 3.8 or higher
- Terminal/command line access
- Text editor or IDE (VS Code recommended)
- **Anthropic API key** (required for live LLM demonstrations with Claude)

**Knowledge Prerequisites:**
- Basic Python programming
- Understanding of LLM/AI concepts
- Familiarity with security principles (helpful but not required)

**Optional:**
- Visual demo dependencies (Streamlit, Jupyter, Rich) for enhanced presentations

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd xconf

# Start with Level 1
cd level-1-malicious-email

# Set up your Anthropic API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Install dependencies
pip install -r requirements.txt

# Run the attack demo
python3 exploit.py

# Run the defense demo
python3 agent_secure.py

# For visual demos
streamlit run app.py
```

---

## 📖 Workshop Materials

### Presentation Slides

- [`llm_attack_vectors_presentation (2).html`](llm_attack_vectors_presentation%20(2).html) - Main workshop presentation
- [`Prompt injection explanation.docx`](Prompt%20injection%20explanation.docx) - Detailed explanation with ShopBot scenario
- [`Prompt Injection.docx`](Prompt%20Injection.docx) - Attack vectors and examples

### Hands-On Labs

- **Level 1:** [`level-1-malicious-email/`](level-1-malicious-email/) - Complete CTF challenge with 4 demo modes

---

## 🎨 Demonstration Modes

Each level supports multiple presentation styles:

| Mode | Best For | Setup Time | Visual Impact |
|------|----------|------------|---------------|
| **Command Line** | Quick testing | 0 seconds | ⭐⭐ |
| **Streamlit Web App** | Workshops, live demos | 30 seconds | ⭐⭐⭐⭐⭐ |
| **Jupyter Notebook** | Self-paced learning | 1 minute | ⭐⭐⭐⭐ |
| **Rich Terminal** | Conference talks | 10 seconds | ⭐⭐⭐⭐ |

**💡 Pro Tip:** Start with command line (no installation), then add visual modes as needed.

---

## 🎯 Core Concept: The Trust Boundary Shift

```
Traditional Applications:  User ↔ Server
Agentic Applications:      LLM ↔ Tools
```

In agentic systems, **data becomes code**, fundamentally changing how we approach security.

---

## 🛡️ Key Defense Patterns

### 1. Dual-LLM Pattern (Level 1)

Separate data extraction from privileged execution:

```
┌─────────────────────────────────────────────────┐
│ Low-Privilege LLM (Parser)                      │
│ - Reads untrusted data                          │
│ - Outputs structured JSON only                  │
│ - NO access to sensitive tools                  │
└────────────┬────────────────────────────────────┘
             │ Sanitized data
             ▼
┌─────────────────────────────────────────────────┐
│ High-Privilege LLM (Executor)                   │
│ - Processes validated data                      │
│ - HAS access to privileged operations           │
│ - Never sees raw untrusted input                │
└─────────────────────────────────────────────────┘
```

### 2. Structural Constraints (Level 2)

Use schema validation to enforce data structure:
- Pydantic models with strict types
- Database-level privilege isolation
- Least-privilege principle

### 3. Output Sanitization (Level 3)

Never trust agent output before rendering:
- Strip markdown images
- Validate URLs
- Content security policies

### 4. Runtime Monitoring (Level 4)

Implement circuit breakers for autonomous operations:
- Execution limits
- Token budgets
- Recursive call detection

---

## 📦 Repository Structure

```
xconf/
├── README.md                                    # This file
├── llm_attack_vectors_presentation (2).html    # Main slides
├── Prompt injection explanation.docx            # ShopBot scenarios
├── Prompt Injection.docx                        # Attack vectors
├── level-1-malicious-email/                     # ✅ VALIDATED & COMPLETE
│   ├── README.md                # Level documentation
│   ├── VALIDATION_REPORT.md     # 🆕 Complete security validation
│   ├── QUICKSTART.md            # 5-minute quick start
│   ├── VISUAL_DEMOS.md          # Demo mode comparison
│   ├── agent.py                 # Vulnerable implementation
│   ├── agent_secure.py          # Secure implementation (Dual-LLM)
│   ├── exploit.py               # Attack demonstration
│   ├── demo_complete.py         # 🆕 Comprehensive demo script
│   ├── app.py                   # Streamlit web app (5 tabs)
│   ├── demo_rich.py             # Rich terminal demo
│   ├── Level_1_Interactive_Tutorial.ipynb  # Jupyter tutorial
│   ├── test_security.py         # 9 automated security tests
│   ├── tools.py                 # Simulated APIs
│   └── data/                    # Email samples & credentials
├── level-2-poisoned-resume/     # 🚧 Planned
├── level-3-s3-exfiltration/     # 🚧 Planned
└── level-4-chaos-calendar/      # 🚧 Planned
```

---

## 🤝 Contributing

Want to add more levels or improve existing ones?

1. Each level should be self-contained in its own directory
2. Include: vulnerable agent, exploit, secure implementation, tests, docs
3. Support multiple demo modes where possible
4. Follow the existing structure from Level 1

---

## 📄 License

Educational material for XConf workshop on LLM security.

---

## 🔗 Additional Resources

### External Reading
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Simon Willison's Prompt Injection Blog](https://simonwillison.net/series/prompt-injection/)
- [LangChain Security Best Practices](https://python.langchain.com/docs/security)

### Related Projects
- [Gandalf Prompt Injection Game](https://gandalf.lakera.ai/)
- [Prompt Injection Primer](https://github.com/jthack/PIPE)

---

## ✨ Key Takeaways

### The Problem
Traditional security controls (input validation, SQL injection prevention, XSS filters) are **insufficient** because LLMs interpret natural language as instructions.

### The Solution
**Defense in Depth for Agentic Systems:**

1. **Layer 1:** Input Sanitization (Dual-LLM pattern)
2. **Layer 2:** Execution Controls (Least privilege, egress filtering)
3. **Layer 3:** Output Sanitization (Content validation)
4. **Layer 4:** Runtime Monitoring (Circuit breakers, budgets)

### The Result
**Immediately actionable defenses** that you can implement in production today.

---

## 🎉 Quick Start Summary

**Want to see it in action right now?**

```bash
cd level-1-malicious-email

# Option 1: No installation required - Basic demo
python3 exploit.py              # See the attack
python3 agent_secure.py         # See the defense
python3 demo_complete.py        # Complete walkthrough

# Option 2: Visual demos (requires dependencies)
pip install -r requirements.txt
streamlit run app.py            # Interactive web app
jupyter notebook Level_1_Interactive_Tutorial.ipynb  # Tutorial

# Option 3: Run automated tests
pip install pytest
pytest test_security.py -v      # 9 tests, 100% pass rate
```

**That's it!** Choose your preferred mode:
- 💻 **Command line** - Works immediately, no setup
- 🌐 **Web app** - Best for workshops and presentations
- 📓 **Jupyter** - Self-paced learning with interactive cells
- ✅ **Tests** - Verify all security controls

---

## 📞 Support

For questions, issues, or feedback:
- Create an issue in this repository
- Review the individual level README files
- Check the VISUAL_DEMOS.md for setup help

---

**Built with ❤️ for XConf 2026**

*Securing the next generation of AI applications, one agent at a time.*
