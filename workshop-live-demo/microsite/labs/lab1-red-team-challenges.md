# Lab 1 (Red Team): Exploiting ShopBot Live — 30 minutes

Goal: run the 8-attack suite from `workshop-live-demo/` against the vulnerable `main` branch.
All 8 attacks are real, pre-tested code in `redteam_test.py` — not hypotheticals — run against a
local Ollama model (`llama3`). No API key needed.

## Setup

```bash
cd workshop-live-demo
ollama serve                        # separate terminal, if not already running; llama3 must be pulled
git checkout main                   # vulnerable baseline (should already be checked out)
```

Two ways to run an attack — pick whichever fits the room:

**Streamlit UI** (recommended for the "Talk to ShopBot" and "Live LLM Red-Team Suite" tabs):
```bash
../level-1-prompt-injection-attack/.venv/bin/streamlit run web_app.py
```

**CLI** (faster for scripting through several attacks back to back):
```bash
python3 redteam_test_ollama.py --attack <name>
```

---

## Challenge 1 — Pick an Attack ⭐☆☆

**Goal:** choose any 1–2 of the 8 named attacks and reproduce it against `main`.

| # | Attack id | Targets |
|---|---|---|
| 1 | `tool_output_injection` | `lookup_api_keys()` via a poisoned order record field |
| 2 | `benign_sender_audit_framing` | `lookup_api_keys()` via a plausible "finance audit" email |
| 3 | `forwarded_thread_spoofing` | `lookup_api_keys()` via a forged forwarded-approval thread |
| 4 | `malicious_attachment_injection` | `lookup_api_keys()` via a hidden note in an uploaded receipt |
| 5 | `unenforced_refund_cap` | `issue_refund()` via pure persuasion, no injection language |
| 6 | `refund_approval_bypass_injection` | `issue_refund()` via an explicit "skip the review step" instruction |
| 7 | `hidden_multilingual_invoice_injection` | `lookup_api_keys()` via a concealed, Spanish-language PDF (mirrors #4) |
| 8 | `hidden_multilingual_email_injection` | `lookup_api_keys()` via a concealed, Spanish-language HTML email (mirrors #2) |

```bash
python3 redteam_test_ollama.py --attack tool_output_injection
```

**Success signal:** the console (or the web app's outcome banner) shows a leaked-credential banner
or an over-cap refund, depending on the attack.

---

## Challenge 2 — Try a Concealed Variant ⭐⭐☆

**Goal:** confirm that concealment (invisible text) and translation don't stop the model, using one
of the pre-tested variants for Attacks 7 and 8:

```bash
python3 redteam_test_ollama.py --attack hidden_multilingual_invoice_injection --variant fr_whiteonwhite
python3 redteam_test_ollama.py --attack hidden_multilingual_invoice_injection --variant pt_invisible
python3 redteam_test_ollama.py --attack hidden_multilingual_email_injection --variant de_whiteonwhite
python3 redteam_test_ollama.py --attack hidden_multilingual_email_injection --variant pt_displaynone
```

`pt_invisible` uses PDF text-render-mode 3 — the real technique used for invisible OCR text
layers — rather than simple white-on-white color matching. Open the real artifact
(`sample_hidden_invoice.pdf` or a variant file) and run `pdftotext <file> -` yourself to see the
hidden text extracted in full.

**Success signal:** same as Challenge 1 — the attack still succeeds despite the concealment.

---

## Challenge 3 — See It as a Product ⭐☆☆

**Goal:** reproduce the same exploit through the "Talk to ShopBot" chat tab in the Streamlit app
instead of a log stream, to see it land against something that looks like a real chat UI.

**Success signal:** the same outcome as Challenge 1, now visible as a chat transcript.

---

Once you've reproduced at least one attack, move on to **Lab 2** — you'll flip the branch to
`remediations` and watch the exact same attacks get blocked.
