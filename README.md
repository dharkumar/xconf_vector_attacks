# Breaking & Defending ShopBot: AI-Age Attack Vectors for LLM-Powered Agents

**A Hands-On CTF-Style Workshop on LLM Security**

---

## 🎯 Workshop Overview

This workshop teaches developers and security engineers how to **secure LLM-powered agentic applications** against real-world attacks through a unified narrative: **ShopBot**, an AI-powered e-commerce customer support platform.

Through hands-on CTF challenges, you'll learn to exploit and defend against **4 distinct prompt injection attack vectors** using a single, cohesive application context.

### Why This Matters

Organizations are rapidly deploying LLM agents with access to:
- Internal tools and databases (order systems, payment gateways)
- Privileged APIs (refund processing, customer data)
- Sensitive credentials (Stripe keys, admin tokens)
- Autonomous decision-making capabilities

**Traditional security controls fail** because LLMs interpret natural language as instructions. This workshop provides immediately actionable defenses for real threats.

---

## 🏆 Flagship Showcase — Start Here for Live Demos

**[`flagship-showcase/`](flagship-showcase/)** is a tightly-scoped,
e-commerce-styled companion app built for presenting to a live audience —
one curated attack per major category (5 total), each with a working
🔴 Vulnerable / 🟢 Protected toggle, instead of the full ~21-scenario
catalog spread across this repo. Everything else stays available for
attendees to explore after the talk.

| # | Scenario | Category | Source app |
|---|----------|----------|------------|
| 1 | **Prompt Injection** | The instruction is right there in the text | `workshop-live-demo` |
| 2 | **Attachment / Concealment** | Hidden + multilingual evasion | `workshop-live-demo` |
| 3 | **Tool Chaining** | A low-risk read tool chained into a high-risk write tool | `tool_chain_attack` |
| 4 | **RAG Poisoning** | Dormant until a semantically-similar query retrieves it | `rag_poisoning_attack` |
| 5 | **Business-Logic Abuse** | Not a prompt injection at all — an unenforced policy limit | `workshop-live-demo` |

Scenario 5 is deliberately included as a closing contrast: it shows that
not every exploit needs clever injection language — a $500 refund cap that
only exists as a sentence in the system prompt is just as exploitable as
any hidden payload.

### ⚙️ Installation Guide (flagship-showcase)

**Prerequisites**
- Python 3.13
- [Ollama](https://ollama.com) installed locally — no Anthropic API key needed, everything runs against local models

```bash
# 1. One-time: pull the two local models used across scenarios (~9GB total)
ollama serve                       # leave running in its own terminal
ollama pull llama3                 # scenarios 1, 2, 5
ollama pull mistral                # scenarios 3, 4

# 2. Set up the app's own virtual environment
cd flagship-showcase
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Run (always via the venv's own streamlit, not a global install)
.venv/bin/streamlit run app.py --server.port 8506
```

Then open `http://localhost:8506`. For why scenarios 3/4 are pinned to
`mistral` instead of `llama3`, and how the app unifies three differently
built backends into one UI, see
[`flagship-showcase/README.md`](flagship-showcase/README.md). For install
steps for every other app in this repo, see [`STARTUP.md`](STARTUP.md).

---

## 🎓 Learning Objectives

By the end of this workshop, attendees will:

1. ✅ Understand how data becomes code in LLM applications
2. ✅ Recognize 4 distinct attack delivery mechanisms (indirect, direct, multimodal, stored)
3. ✅ Implement the Dual-LLM defense pattern
4. ✅ Apply privilege separation, egress filtering, and input sanitization
5. ✅ Validate security controls through automated testing

---

## 🏗️ The ShopBot Application

**ShopBot** is an AI-powered customer support agent for an e-commerce platform with the following capabilities:

**Core Functions:**
- Process customer support emails
- Track order status and validate refund requests
- Verify product returns (text and images)
- Manage customer profiles and preferences

**Privileged Operations:**
```python
check_order_status(order_id: str) -> dict
issue_refund(user_id: str, amount_usd: float) -> dict
send_customer_email(to: str, subject: str, body: str) -> dict
lookup_api_keys() -> str  # [SENSITIVE - Attack Target]
```

**Sensitive Data at Risk:**
- Stripe payment gateway API keys
- AWS S3 credentials
- Admin portal tokens
- Customer payment information

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
cd xconf_vector_attacks

# Start with Level 1: ShopBot Prompt Injection Attack
cd level-1-prompt-injection-attack

# Set up your Anthropic API key (optional for simulation mode)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Install dependencies (optional for basic demos)
pip install -r requirements.txt

# Run the interactive chat demos
python3 chat_agent.py              # Vulnerable CLI chat
python3 chat_agent_secure.py       # Secure CLI chat

# For visual demos
streamlit run chat_app.py          # 5-tab web interface
```

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

## 🎯 Core Concept: Data Becomes Code

```
Traditional Applications:
  User Input → Validation → SQL/Logic → Output
  (Clear separation: data ≠ code)

LLM Agentic Applications:
  User Input → LLM Context → Natural Language Instructions → Tool Execution
  (No separation: data = code)
```

In agentic systems, **any text can become executable instructions**, fundamentally changing how we approach security.

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

### 2. Input Classification & Schema Enforcement (Level 2)

Detect threats before LLM processing:
- Pre-LLM keyword detection for known attack patterns
- Pydantic models with strict types for all tool calls
- Hard-coded business logic limits (max refund amounts)
- Human-in-the-loop workflows for sensitive operations

### 3. Multimodal Sanitization (Level 3)

Never trust visual inputs:
- Separate OCR extraction from VLM analysis
- Deterministic classifiers for critical decisions
- Image sanitization pipelines (strip EXIF, reprocess)
- Content filtering on extracted text

### 4. Context Tagging & Delayed Sanitization (Level 4)

Mark and sanitize untrusted data sources:
- Tag all external data (DB, APIs, files) as untrusted
- Sanitize at both ingestion AND retrieval time
- Schema validation with strict field constraints
- Audit logging for suspicious patterns

---

## 📦 Repository Structure

```
xconf_vector_attacks/
├── README.md                                # This file
├── STARTUP.md                               # Install/run guide for every app below
├── WORKSHOP_SPEC.md                         # Original full specification document
├── Prompt injection explanation.docx        # ShopBot scenarios
├── Prompt Injection.docx                    # Attack vectors
│
├── flagship-showcase/                       # ⭐ Curated 5-scenario live-demo app -- start here
│   ├── app.py                   # Streamlit entrypoint
│   ├── adapters.py              # Normalizes the 3 different backends below into one shape
│   ├── scenario_registry.py     # Per-scenario blurbs/payloads (the 5 flagship attacks)
│   ├── ui_components.py         # Chat bubble, verdict, tool-call rendering
│   ├── tests/
│   └── README.md
│
├── level-1-prompt-injection-attack/         # Shared venv + Level 1 attack/defense scripts
│   ├── chat_agent.py            # Vulnerable CLI chat agent
│   ├── chat_agent_secure.py     # Secure CLI chat agent
│   ├── chat_app.py              # Streamlit web app (5 tabs)
│   ├── agent.py / agent_secure.py / exploit.py   # Legacy email-based demo
│   ├── test_security.py         # Automated security tests
│   └── data/
│       ├── customer_emails.json # 8 emails (4 legit + 4 attacks)
│       ├── orders.json          # 7 customer orders
│       └── api_keys.md          # Sensitive credentials (target)
│
├── level-2-shopbot-advanced-attacks/        # 6 CTF-style evasion challenges (regex/string checks, no LLM call)
│   ├── chat_app.py               # Streamlit challenge UI
│   ├── challenges/                # The 6 attack-pattern challenges
│   ├── defense_patterns.py
│   └── data/
│
├── tool_chain_attack/                       # Chaining a low-risk read tool into a high-risk write tool
│   ├── demo_attack_1.py / demo_attack_2.py / demo_attack_3.py
│   ├── vulnerable_agent.py / secure_agent.py     # + _ollama.py variants for local models
│   ├── visual_demo_app.py       # Streamlit visual demo
│   └── shopbot_tools.py         # Shared tool implementations + call history
│
├── rag_poisoning_attack/                    # Poisoning a knowledge base via real embedding retrieval
│   ├── demo_attack_1.py .. demo_attack_4.py
│   ├── vulnerable_rag_agent.py / secure_rag_agent.py   # + _ollama.py variants
│   ├── visual_demo_app.py       # Streamlit visual demo
│   └── knowledge_base_tools.py  # ChromaDB + sentence-transformers retrieval
│
└── workshop-live-demo3/                     # Colleague's snapshot of the main red-team suite (8 attacks)
    ├── web_app.py                # 3-tab product-style chat UI + live red-team suite
    ├── redteam_test_ollama.py    # Backs flagship-showcase scenarios 1, 2, 5
    └── PRESENTER_GUIDE.md        # Full attack x remediation breakdown
```

⚠️ `workshop-live-demo3/` has no git repository of its own — see `STARTUP.md`
for why its branch-toggle tab needs care before you use it.

---

## 📄 License

Educational material for XConf workshop on LLM security.

---

## 🔗 Additional Resources

### Foundational Resources
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Simon Willison's Prompt Injection Blog](https://simonwillison.net/series/prompt-injection/)
- [Anthropic - Claude Safety Best Practices](https://docs.anthropic.com/claude/docs/security)

### Related CTF Challenges
- [Gandalf Prompt Injection Game](https://gandalf.lakera.ai/)
- [Prompt Injection Primer (PIPE)](https://github.com/jthack/PIPE)

---

## ✨ Key Takeaways

### The Problem
Traditional security controls (input validation, SQL injection prevention, XSS filters) are **insufficient** because:
- LLMs interpret natural language as instructions
- No hardware-level privilege separation between data and code
- Every text input is a potential execution vector

### The Solution
**Defense in Depth for Agentic Systems:**

1. **Layer 1:** Input Sanitization (Dual-LLM pattern, context tagging)
2. **Layer 2:** Execution Controls (Least privilege, egress filtering)
3. **Layer 3:** Output Sanitization (Content validation, schema enforcement)
4. **Layer 4:** Runtime Monitoring (Circuit breakers, audit logging)

### The Result
**Immediately actionable defenses** that you can implement in production today.

---

## 🎉 Quick Start Summary

**Want to see it in action right now?**

```bash
cd level-1-prompt-injection-attack

# Option 1: Interactive CLI Chat (Fastest - No Setup!)
python3 chat_agent.py              # Vulnerable chat agent
python3 chat_agent_secure.py       # Secure chat agent

# Option 2: Streamlit Web App (Best for Workshops!)
streamlit run chat_app.py          # 5 interactive tabs with copyable attacks

# Option 3: Legacy Email-Based Demos (Still Available)
python3 exploit.py                 # Email attack demo
python3 agent_secure.py            # Email defense demo
```

**Choose your preferred mode:**
- 💻 **CLI Chat** - Interactive, immediate, no setup
- 🌐 **Streamlit Web App** - Best for workshops and presentations
- 📓 **Legacy Demos** - Email-based attacks (original approach)
- ✅ **Tests** - Verify all security controls

---

## 📞 Support

For questions, issues, or feedback:
- Create an issue in this repository
- Review **WORKSHOP_SPEC.md** for detailed specifications
- Check individual level README files for specific documentation

---

**Built with ❤️ for XConf 2026**

*Securing the next generation of AI applications through hands-on learning.*

**Workshop Theme:** Breaking & Defending ShopBot - 4 Attack Vectors for LLM-Powered Agents
