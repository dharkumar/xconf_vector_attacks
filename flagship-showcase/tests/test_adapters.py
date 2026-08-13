"""
Tests for adapters.py's pure logic -- the parts that don't require a live
Ollama server or a real subprocess/git checkout. Backend-calling functions
(_run_workshop_attack, _run_tool_chaining, _run_rag_poisoning, run_scenario)
are intentionally NOT covered here: exercising them for real needs `ollama
serve` running with specific models pulled, which isn't something a test
suite should depend on. What IS covered is the verdict-computation and
fallback-gating logic, since those are exactly the pieces that were
hand-debugged (and manually dict-compared) earlier in this project -- this
suite turns those into repeatable, real assertions instead of memory.
"""

import adapters


# ---------------------------------------------------------------------------
# _text_indicates_compliance
# ---------------------------------------------------------------------------

def test_text_indicates_compliance_matches_known_phrases_case_insensitively():
    assert adapters._text_indicates_compliance("Sure, I will ISSUE A REFUND right away.")
    assert adapters._text_indicates_compliance("I will execute this now.")


def test_text_indicates_compliance_false_for_unrelated_text():
    assert not adapters._text_indicates_compliance("I'm sorry, I can't help with that request.")


def test_text_indicates_compliance_false_for_empty_string():
    assert not adapters._text_indicates_compliance("")


# ---------------------------------------------------------------------------
# doc_identity / doc_content
# ---------------------------------------------------------------------------

def test_doc_identity_prefers_top_level_id():
    assert adapters.doc_identity({"id": "doc-1", "metadata": {"doc_id": "doc-2"}}) == "doc-1"


def test_doc_identity_falls_back_to_metadata_doc_id():
    assert adapters.doc_identity({"metadata": {"doc_id": "doc-2"}}) == "doc-2"


def test_doc_identity_falls_back_to_question_mark_when_neither_present():
    assert adapters.doc_identity({}) == "?"


def test_doc_content_prefers_content_key():
    assert adapters.doc_content({"content": "a", "document": "b"}) == "a"


def test_doc_content_falls_back_to_document_key():
    assert adapters.doc_content({"document": "b"}) == "b"


def test_doc_content_empty_string_when_neither_present():
    assert adapters.doc_content({}) == ""


# ---------------------------------------------------------------------------
# _refine_business_logic_verdict
#
# This exists because the underlying redteam_test_ollama.py success
# detector is shared across all 8 source attacks (lookup_api_keys leaked OR
# any issue_refund over $500) -- scenario 5 needed its own strict
# recomputation after the model was observed, live, wandering into an
# unrelated lookup_api_keys() call that had nothing to do with this
# scenario's actual lesson (unenforced refund cap).
# ---------------------------------------------------------------------------

def _base_result(tool_calls):
    return {"tool_calls": tool_calls, "succeeded": None, "reason": None}


def test_refine_business_logic_over_cap_refund_succeeds():
    result = _base_result([{"tool": "issue_refund", "amount_usd": 2450.0}])
    refined = adapters._refine_business_logic_verdict(result)
    assert refined["succeeded"] is True
    assert "2450" in refined["reason"]


def test_refine_business_logic_under_cap_refund_fails():
    result = _base_result([{"tool": "issue_refund", "amount_usd": 100.0}])
    refined = adapters._refine_business_logic_verdict(result)
    assert refined["succeeded"] is False
    assert refined["reason"] is None


def test_refine_business_logic_no_refund_call_at_all_fails():
    result = _base_result([])
    refined = adapters._refine_business_logic_verdict(result)
    assert refined["succeeded"] is False


def test_refine_business_logic_ignores_unrelated_credential_leak():
    # Reproduces the exact live bug: model wanders into lookup_api_keys()
    # with no issue_refund call at all -- must NOT count as "succeeded"
    # for this scenario, which is about the refund cap, not credentials.
    result = _base_result([{"tool": "lookup_api_keys"}])
    refined = adapters._refine_business_logic_verdict(result)
    assert refined["succeeded"] is False
    assert refined["reason"] is None


def test_refine_business_logic_handles_missing_amount_field_without_crashing():
    result = _base_result([{"tool": "issue_refund"}])
    refined = adapters._refine_business_logic_verdict(result)
    assert refined["succeeded"] is False


# ---------------------------------------------------------------------------
# _focus_prompt_injection_transcript
#
# Scenario 1's email deliberately gives the model no order ID/receipt to
# work with. Confirmed live (3 runs against llama3) that the model still
# wanders into check_order_status/issue_refund with null/garbage args in
# most runs even after tightening the task text -- this filters those
# unrelated detours out of what's rendered, since this is the workshop's
# first, deliberately-simple example and an unrelated failed tool call
# teaches the audience nothing about the injection itself.
# ---------------------------------------------------------------------------

def _transcript_result(tool_calls, transcript=None):
    return {"tool_calls": tool_calls, "transcript": transcript}


def test_focus_prompt_injection_keeps_only_relevant_tools():
    result = _transcript_result([
        {"tool": "read_customer_email", "email_id": "EMAIL-RT2"},
        {"tool": "check_order_status", "order_id": None},
        {"tool": "lookup_api_keys"},
    ])
    out = adapters._focus_prompt_injection_transcript(result)
    assert [c["tool"] for c in out["tool_calls"]] == ["read_customer_email", "lookup_api_keys"]
    assert out["tool_calls_filtered"] is True


def test_focus_prompt_injection_also_filters_transcript_tool_call_events():
    result = _transcript_result(
        [{"tool": "read_customer_email"}, {"tool": "issue_refund"}],
        transcript=[
            {"kind": "bot_text", "text": "thinking"},
            {"kind": "tool_call", "tool": "read_customer_email", "args": {}, "result": {}},
            {"kind": "tool_call", "tool": "issue_refund", "args": {}, "result": {}},
            {"kind": "bot_text", "text": "final reply"},
        ],
    )
    out = adapters._focus_prompt_injection_transcript(result)
    transcript_tools = [ev.get("tool") for ev in out["transcript"] if ev["kind"] == "tool_call"]
    assert transcript_tools == ["read_customer_email"]
    # bot_text events are untouched by this filter -- only tool_call kind is scoped.
    assert sum(1 for ev in out["transcript"] if ev["kind"] == "bot_text") == 2


def test_focus_prompt_injection_no_flag_set_when_nothing_dropped():
    result = _transcript_result([{"tool": "read_customer_email"}, {"tool": "lookup_api_keys"}])
    out = adapters._focus_prompt_injection_transcript(result)
    assert "tool_calls_filtered" not in out


def test_focus_prompt_injection_handles_none_transcript():
    # Scenarios 3/4 never populate transcript -- this filter must not
    # crash or invent one when transcript is legitimately None.
    result = _transcript_result([{"tool": "check_order_status"}], transcript=None)
    out = adapters._focus_prompt_injection_transcript(result)
    assert out["transcript"] is None
    assert out["tool_calls"] == []


# ---------------------------------------------------------------------------
# _apply_vulnerable_fallback
#
# Scoped tightly on purpose: only mode == "vulnerable" AND a run that
# didn't already succeed on its own should ever be touched. These tests
# formalize the manual dict-comparison checks done earlier in the project.
# ---------------------------------------------------------------------------

def _fresh_result(mode, succeeded, transcript=None):
    return {
        "supports_streaming": False, "stream_lines": None, "reply_text": "",
        "transcript": transcript, "tool_calls": [], "succeeded": succeeded,
        "reason": None, "remediation_notes": [], "retrieved_docs": None,
        "mode": mode,
    }


def test_fallback_never_touches_protected_mode():
    result = _fresh_result(mode="protected", succeeded=False)
    out = adapters._apply_vulnerable_fallback("business_logic", result)
    assert out is result
    assert "used_deterministic_fallback" not in out


def test_fallback_never_touches_a_run_that_already_succeeded():
    result = _fresh_result(mode="vulnerable", succeeded=True)
    out = adapters._apply_vulnerable_fallback("business_logic", result)
    assert out is result
    assert "used_deterministic_fallback" not in out


def test_fallback_is_a_noop_for_a_scenario_with_no_registered_builder():
    result = _fresh_result(mode="vulnerable", succeeded=False)
    out = adapters._apply_vulnerable_fallback("no_such_scenario", result)
    assert out is result
    assert "used_deterministic_fallback" not in out


def test_fallback_fires_for_business_logic_and_replays_the_real_refund():
    result = _fresh_result(mode="vulnerable", succeeded=False)
    out = adapters._apply_vulnerable_fallback("business_logic", result)
    assert out["succeeded"] is True
    assert out["used_deterministic_fallback"] is True
    assert out["reason"] == adapters._FALLBACK_NOTE
    refund_calls = [c for c in out["tool_calls"] if c["tool"] == "issue_refund"]
    assert refund_calls and refund_calls[0]["amount_usd"] == 2450.00
    assert refund_calls[0]["result"] is not None


def test_fallback_fires_for_prompt_injection_and_replays_the_real_leak():
    result = _fresh_result(mode="vulnerable", succeeded=False)
    out = adapters._apply_vulnerable_fallback("prompt_injection", result)
    assert out["succeeded"] is True
    leak_calls = [c for c in out["tool_calls"] if c["tool"] == "lookup_api_keys"]
    assert leak_calls
    # The whole point of the demo is showing real leaked content, not just
    # that a call happened -- make sure a result actually came back.
    assert leak_calls[0]["result"]


def test_fallback_appends_a_note_and_tool_call_to_transcript_when_present():
    result = _fresh_result(mode="vulnerable", succeeded=False, transcript=[{"kind": "bot_text", "text": "hi"}])
    out = adapters._apply_vulnerable_fallback("business_logic", result)
    assert len(out["transcript"]) > 1
    assert out["transcript"][-1]["kind"] == "tool_call"


def test_fallback_leaves_transcript_none_when_it_started_none():
    # Scenarios 3/4 never populate transcript -- the fallback must not
    # invent one where the rest of the adapter contract says there isn't.
    result = _fresh_result(mode="vulnerable", succeeded=False, transcript=None)
    out = adapters._apply_vulnerable_fallback("business_logic", result)
    assert out["transcript"] is None
