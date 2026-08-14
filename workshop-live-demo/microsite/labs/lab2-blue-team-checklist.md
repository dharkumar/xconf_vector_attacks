# Lab 2 (Blue Team): Hardening ShopBot Live — 35 minutes

Goal: use the branch switcher to flip `workshop-live-demo/` from vulnerable to protected and watch
the same attacks you ran in Lab 1 get blocked. Your pass/fail signal is the app/CLI's own outcome
banner, derived live from the tool-call log — not a canned answer.

```bash
cd workshop-live-demo
```

---

## Task A — Confirm the Exploit

Pick one of the 8 attacks from Lab 1, run it on `main`, and note the exact outcome (which tool got
called, with what arguments, and what the model's final reply was).

```bash
git checkout main
python3 redteam_test_ollama.py --attack <name>
```

**Checklist:**
- [ ] Attack succeeds on `main` (credential leak, or a refund over the $500 cap)

---

## Task B — Flip the Branch

Switch to the `remediations` branch (via the Streamlit app's branch radio, or `git checkout
remediations` on the CLI) and re-run the identical attack.

```bash
git checkout remediations
python3 redteam_test_ollama.py --attack <same name as Task A>
```

**Checklist:**
- [ ] The attack is blocked
- [ ] You can identify which lettered remediation fired (A, B, C, and/or D — the outcome banner
      names it)

---

## Task C — Find the Fix

Open `tools_secure.py` and find the exact function that stopped your attack. Map it to its letter:

| Letter | Name | Function(s) to look for |
|---|---|---|
| A | Dual-LLM extraction | `_extract()`, `check_order_status_secure()`, `read_uploaded_receipt_secure()` |
| B | Least privilege | `AVAILABLE_FUNCTIONS_SECURE` — note the absent `lookup_api_keys` key |
| C | Hard-coded refund cap | `issue_refund_secure()`, `REFUND_AUTO_APPROVAL_LIMIT_USD` |
| D | Suspicious-sender escalation | `read_customer_email_secure()`, the `_last_email_flag` check at the top of `issue_refund_secure()` |

**Checklist:**
- [ ] You've read the specific function and can explain in one sentence why it stops your attack

**Stretch:** try one of Attack 3's or Attack 8's runs a second time — both have a documented case
in `PRESENTER_GUIDE.md` where a judgment-based remediation (D) didn't fire the same way every run,
and a hard-coded backstop (B or C) caught the attempt anyway. See if you can reproduce that.

---

## Reminder

Remediation D is judgment-based and `llama3` isn't fully deterministic. If a run doesn't reproduce
the documented outcome, re-run it once before assuming something's broken.
