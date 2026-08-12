# Flagship Showcase

A tightly-scoped, e-commerce-styled companion to the full workshop apps:
only 5 curated attacks (one per major category), each with a working
vulnerable/protected toggle, so a live audience sees the essential story
without the full ~21-scenario catalog. The other scenarios stay in their
original folders for participants to explore after the talk.

## The 5 scenarios

1. **Prompt Injection** (from `workshop-live-demo`)
2. **Attachment / Concealment** (from `workshop-live-demo`)
3. **Tool Chaining** (from `tool_chain_attack`)
4. **RAG Poisoning** (from `rag_poisoning_attack`)
5. **Business-Logic Abuse** (from `workshop-live-demo`) — deliberately not a
   prompt-injection attack, included as a closing contrast

## Run

```bash
cd flagship-showcase
python3.13 -m venv .venv          # first time only
.venv/bin/pip install -r requirements.txt
ollama serve                      # separate terminal, if not already running
ollama pull llama3                # scenarios 1, 2, 5
ollama pull mistral                # scenarios 3, 4 -- see note below
.venv/bin/streamlit run app.py --server.port 8506
```

No `ANTHROPIC_API_KEY` needed — everything runs against local Ollama.

## Why scenarios 3/4 are pinned to `mistral`, not `llama3`

`llama3` doesn't support Ollama's native `tools=[]` parameter at all (a
400 error) — this is a real, pre-existing limitation of `tool_chain_attack`
and `rag_poisoning_attack`'s Ollama backends, confirmed while building this
app, not something introduced here. `mistral` accepts the parameter but
often narrates a tool call as text (sometimes literally as raw JSON)
instead of emitting a structured call Ollama executes. `adapters.py`
handles this honestly: it treats a clear textual statement of intent to
call the sensitive tool as a legitimate "succeeded" signal on the
vulnerable side — the same fallback `tool_chain_attack`'s own
`demo_attack_1_ollama.py` already uses, extended to scenario 4 as well.

Both modes for scenarios 3/4 are pinned to the same model explicitly
(`adapters.py`, not left to `OLLAMA_MODEL`) so a "the code stopped it"
result is never confounded with "a different model happened to run."

## Architecture

- `scenario_registry.py` — static per-scenario data (blurb, payload, backend kind)
- `adapters.py` — the only file that knows about the 3 different backends;
  normalizes everything to one `ScenarioResult` shape
- `ui_components.py` — chat bubble, typing indicator, verdict/tool-call rendering
- `app.py` — Streamlit entrypoint; only ever reads `ScenarioResult`, never
  imports a backend directly

See the plan file used to build this (referenced in the session that
created it) for the full design rationale, including a real concurrency
hazard (`tool_chain_attack` and `rag_poisoning_attack` share a global
`tool_call_history` list in memory) and its fix (a lock in `adapters.py`).
