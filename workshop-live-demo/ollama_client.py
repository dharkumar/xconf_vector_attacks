"""
Minimal shared Ollama HTTP client + JSON-object extraction, used by both
redteam_test_ollama.py (the main agent loop) and tools_secure.py (the
dual-LLM parser in Remediation A). Kept in one place so both call the same
local model the same way.
"""

import json
import os
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

_decoder = json.JSONDecoder()


def call_ollama(messages, model=None, temperature=0.2):
    payload = json.dumps({
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    return data["message"]["content"]


def extract_json_object(text, required_key=None):
    """Find the first JSON object in `text`, optionally requiring it to
    contain `required_key`. Uses raw_decode (not regex) so it correctly
    handles nested braces, e.g. a nested "args": {...}."""
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = _decoder.raw_decode(text, i)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if required_key is not None and required_key not in obj:
            continue
        return obj
    return None


def extract_json_objects(text, required_key=None):
    """Find every JSON object in `text`, not just the first -- for the
    agent loop, where a model narrating several tool calls in one response
    would otherwise have every call after the first silently dropped.
    extract_json_object (singular) is intentionally left untouched: the
    dual-LLM parser in tools_secure.py always wants exactly one structured
    response and should keep that guarantee."""
    objects = []
    i = 0
    while i < len(text):
        if text[i] != "{":
            i += 1
            continue
        try:
            obj, end = _decoder.raw_decode(text, i)
        except json.JSONDecodeError:
            i += 1
            continue
        if isinstance(obj, dict) and (required_key is None or required_key in obj):
            objects.append(obj)
        i = end
    return objects
