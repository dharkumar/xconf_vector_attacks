# Workshop Startup Guide

How to get `flagship-showcase` — the live-demo app for this workshop —
running on your own laptop.

## Prerequisites

1. **Python 3.13** (the app uses its own virtual environment, so other
   Python versions on your machine won't conflict).
2. **Ollama**, for the free/offline/no-API-key path:
   ```bash
   brew install ollama      # if not already installed
   ollama serve             # leave running in its own terminal
   ollama pull llama3       # ~4.7GB, used as the "vulnerable" model
   ollama pull mistral      # ~4.1GB, used as the "secure" model in a couple of scenarios
   ```
   Both models need to be pulled once — after that everything runs fully
   offline. No Anthropic API key needed.

---

## `flagship-showcase/` — start here for the live audience talk

**What it is:** a curated, e-commerce-styled companion app showing only 5
flagship attacks (one per major category: prompt injection, attachment/
concealment, tool chaining, RAG poisoning, and business-logic abuse), each
with a working vulnerable/protected toggle.

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
