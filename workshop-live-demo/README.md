# Workshop Live Demo -- Indirect Prompt Injection (EMAIL-006)

Standalone, independent of the rest of this repo. Two files, zero setup:
no API key, no venv, no network, no `pip install`. Just `python3 <file>`.
Safe to hand out to a room of 50 without any setup step.

## Delivery flow (~10 minutes)

1. **You run `vulnerable.py` on the projector.** Narrate what's happening
   line by line: the agent reads an email, finds "instructions" inside it,
   and obeys them -- credentials get leaked, a stealth $1 refund goes out.
2. **Hand out both files** (or point participants at this folder). Have
   them run `python3 vulnerable.py` themselves so it's not just something
   they watched -- they saw it happen on their own machine.
3. **Explain the defense** (role separation + escalation -- see the
   docstring at the top of `secure.py`). This is the "reveal" moment.
4. **Have them run `python3 secure.py`.** Same attack email, same tools,
   different outcome. Ask them to find the line where the two functions
   `parse_email()` and `execute()` never pass raw email text to each other
   -- that's the whole defense in one sentence.

## Why deterministic scripts, not a live LLM call

Modern Claude models are already skeptical of this exact injection
wording, so calling a real API here is a coin flip you don't want live in
front of 50 people, and it also requires every laptop to have a working
key + network. These two scripts hardcode the "as-is" and "to-be"
behavior instead, so the before/after contrast is guaranteed to land the
same way every time, on every machine, offline.

If you want to demonstrate the *real* LLM version afterwards for
credibility, use `chat_agent.py` / `chat_agent_secure.py` in
`level-1-prompt-injection-attack/` -- that's a separate, richer demo with
an actual API integration, kept out of this folder on purpose.
