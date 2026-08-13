# AI vector attacks - Workshop Startup Guide

How to get `flagship-showcase` — the live-demo app for this workshop —
running on your own laptop.

## Prerequisites

1. **Python 3.13** (the app uses its own virtual environment, so other
   Python versions on your machine won't conflict).

   macOS:
   ```bash
   brew install python@3.13
   python3.13 --version
   ```

   Linux: install via your package manager (e.g. `apt install python3.13`).

   Windows: install from [python.org](https://www.python.org/downloads/)
   — tick **"Add python.exe to PATH"** during install — or
   `winget install Python.Python.3.13`. Check with `py -3.13 --version`.

2. **poppler**, for `pdftotext` (used by `flagship-showcase` scenario 2 to
   extract text from the hidden-injection PDF):

   macOS:
   ```bash
   brew install poppler
   ```

   Linux: `apt install poppler-utils` (or your distro's equivalent).

   Windows: `choco install poppler` (Chocolatey), `scoop install poppler`
   (Scoop), or download from
   [the poppler-windows releases page](https://github.com/oschwartz10612/poppler-windows/releases)
   and add its `Library\bin` folder to PATH.

3. **Ollama**, for the free/offline/no-API-key path:

   macOS:
   ```bash
   brew install ollama      # if not already installed
   ollama serve             # leave running in its own terminal
   ```

   Windows: download and run the installer from
   [ollama.com/download/windows](https://ollama.com/download/windows) (or
   `winget install Ollama.Ollama`). It installs as a background service and
   starts automatically — no need to run `ollama serve` manually unless
   it's not already running.

   Then, on any OS, pull both models once:
   ```bash
   ollama pull llama3       # ~4.7GB, used as the "vulnerable" model
   ollama pull mistral      # ~4.1GB, used as the "secure" model in a couple of scenarios
   ```
   After that everything runs fully offline. No Anthropic API key needed.

---

## `flagship-showcase/` — start here for the live audience talk

**What it is:** a curated, e-commerce-styled companion app showing only 5
flagship attacks (one per major category: prompt injection, attachment/
concealment, tool chaining, RAG poisoning, and business-logic abuse), each
with a working vulnerable/protected toggle.

**Setup and run — macOS / Linux:**
```bash
cd flagship-showcase
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py --server.port 8506
```

**Setup and run — Windows (PowerShell):**
```powershell
cd flagship-showcase
py -3.13 -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
.venv\Scripts\streamlit.exe run app.py --server.port 8506
```

Needs Ollama running with both `llama3` and `mistral` pulled. No API key
needed. See `flagship-showcase/README.md` for why two models are needed
and how the app unifies three differently-built backends.
