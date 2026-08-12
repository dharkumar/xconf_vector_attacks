# Workshop Startup Guide

How to get every demo running on your own laptop. Read the **Prerequisites**
section once, then jump to whichever app(s) you need.

## Prerequisites

1. **Python 3.13** (each app below uses its own virtual environment, so
   other Python versions on your machine won't conflict).
2. **An Anthropic API key**, for anything that offers a "Claude mode":
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```
   Get one at https://console.anthropic.com/. Everything also has a local
   **Ollama mode** that needs no key and no network — see next point.
3. **Ollama**, for the free/offline/no-API-key path:
   ```bash
   brew install ollama      # if not already installed
   ollama serve             # leave running in its own terminal
   ollama pull llama3       # ~4.7GB, used as the "vulnerable" model everywhere
   ollama pull mistral      # ~4.1GB, used as the "secure" model in a couple of demos
   ```
   Both models need to be pulled once — after that everything runs fully
   offline.

Each app below is self-contained with its own `requirements.txt`. Set one
up like this (shown for `level-2-shopbot-advanced-attacks`, same pattern
everywhere):
```bash
cd level-2-shopbot-advanced-attacks
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run chat_app.py
```

---

## 0. `flagship-showcase/` — start here for the live audience talk

**What it is:** a curated, e-commerce-styled companion app showing only 5
flagship attacks (one per major category: prompt injection, attachment/
concealment, tool chaining, RAG poisoning, and business-logic abuse), each
with a working vulnerable/protected toggle. Built specifically to avoid
overwhelming a live audience with all ~21 scenarios in the full codebase —
everything else below remains available for participants to explore
afterward.

**Setup:**
```bash
cd flagship-showcase
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Run:**
```bash
.venv/bin/streamlit run app.py --server.port 8506
```
Needs `ollama serve` running with both `llama3` and `mistral` pulled. No
API key needed. See `flagship-showcase/README.md` for why two models are
needed and how the app unifies three differently-built backends.

---

## 1. `workshop-live-demo/` — the main red-team suite (8 real attacks)

**What it is:** the primary demo. Three tabs: a product-style chat UI, an
instant no-LLM before/after (EMAIL-006), and a live red-team suite running
8 named attacks against a real local Ollama model — with a branch switch
that toggles between a vulnerable and a remediated version of the *actual
underlying code*, not just a setting.

**Setup:** reuses `level-1-prompt-injection-attack`'s virtual environment
(see below) — nothing extra to install here.

**Run:**
```bash
cd workshop-live-demo
../level-1-prompt-injection-attack/.venv/bin/streamlit run web_app.py --server.port 8501
```
Needs `ollama serve` running with `llama3` pulled (see Prerequisites).

**Reference:** `PRESENTER_GUIDE.md` in this folder has the full attack ×
remediation breakdown.

---

## 2. `level-1-prompt-injection-attack/` — the shared environment + Level 1 scripts

**What it is:** the foundational attack/defense scripts (`agent.py` /
`agent_secure.py`, `chat_agent.py` / `chat_agent_secure.py`), and the
virtual environment that `workshop-live-demo` and `workshop-live-demo3`
both borrow.

**Setup:**
```bash
cd level-1-prompt-injection-attack
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Run examples:**
```bash
.venv/bin/python3 exploit.py                 # scripted EMAIL-006 attack, no key needed
.venv/bin/streamlit run chat_app.py --server.port 8506   # real Claude-backed chat demo
```
See `QUICKSTART.md` / `CHAT_QUICKSTART.md` in this folder for more.

---

## 3. `level-2-shopbot-advanced-attacks/` — 6 advanced evasion challenges

**What it is:** a CTF-style app with 6 challenges (obfuscation, translation,
fictional framing, few-shot hijacking, prompt leakage, tool chaining) —
paste an attack payload and see whether the "hardened" or "secure" filter
catches it. Pure text/regex checks, no live LLM call, so it needs no
Ollama and works instantly.

**Setup:**
```bash
cd level-2-shopbot-advanced-attacks
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Run:**
```bash
.venv/bin/streamlit run chat_app.py --server.port 8503
```
`ANTHROPIC_API_KEY` isn't required for the challenge tabs themselves (they're
string-matching, not live LLM calls).

---

## 4. `tool_chain_attack/` — chaining a low-risk read into a high-risk write

**What it is:** a real, live agent (Claude or Ollama) that demonstrates 3
tool-chaining attacks — e.g. checking an order, then auto-issuing a refund
under an invented "policy," with no re-check in between.

**Setup:**
```bash
cd tool_chain_attack
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt streamlit
```

**Run:**
```bash
.venv/bin/streamlit run visual_demo_app.py --server.port 8504
```
Or CLI: `.venv/bin/python3 demo_attack_1.py`, `demo_attack_2.py`,
`demo_attack_3.py`, then `secure_agent.py` / `demo_secure_comparison.py`
for the fix. Ollama mode defaults to `llama3` (vulnerable) / `mistral`
(secure).

---

## 5. `rag_poisoning_attack/` — poisoning a knowledge base, not a single document

**What it is:** 4 attacks where the poison sits dormant in a vector-search
knowledge base and only surfaces when an unrelated-looking later query
happens to retrieve it — genuine embedding similarity search (ChromaDB +
sentence-transformers), not a single document handed to the agent.

**Setup:**
```bash
cd rag_poisoning_attack
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```
First run downloads a ~90MB embedding model (`all-MiniLM-L6-v2`) — do this
once **before** you're in front of a room, not live.

**Run:**
```bash
.venv/bin/streamlit run visual_demo_app.py --server.port 8505
```
Or CLI: `.venv/bin/python3 demo_attack_1.py` through `demo_attack_4.py`
(and the `_ollama.py` counterparts). Ollama mode defaults to `llama3`
(vulnerable) / `mistral` (secure).

---

## 6. `workshop-live-demo3/` — ⚠️ do not use the branch toggle

**What it is:** a colleague's snapshot of an earlier version of
`workshop-live-demo`, with its own visual theme applied on top.

**Known issue — please read before running this one:** this folder has
**no git repository of its own**. Its "vulnerable ↔ remediated" branch
toggle calls `git checkout <branch>` under the hood, and with no local
repo here, that command falls through to **the shared top-level repo**
that everyone's other demos live in. Clicking that toggle could check out
a branch across the whole shared project out from under every other demo
folder, or fail loudly if the branch doesn't exist.

**If you want to look at this one, only use its first tab** (the instant
EMAIL-006 demo, no branch switching involved). Avoid the red-team suite
tab's branch radio until this is fixed properly.

**Run (if needed):**
```bash
cd workshop-live-demo3
../level-1-prompt-injection-attack/.venv/bin/streamlit run web_app.py --server.port 8502
```

---

## Quick reference

| App | Port | Needs Ollama? | Needs API key? |
|---|---|---|---|
| flagship-showcase (start here for live talks) | 8506 | Yes (llama3 + mistral) | No |
| workshop-live-demo | 8501 | Yes (llama3) | No |
| workshop-live-demo3 ⚠️ | 8502 | Yes (llama3) | No |
| level-2-shopbot-advanced-attacks | 8503 | No | No |
| tool_chain_attack | 8504 | Optional (llama3/mistral) | Optional |
| rag_poisoning_attack | 8505 | Optional (llama3/mistral) | Optional |

All ports above are just examples (`--server.port N`) — Streamlit will
auto-pick the next free port if you omit the flag, so running several at
once on one laptop works fine without collisions.
