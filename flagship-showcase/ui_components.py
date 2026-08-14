"""
Reusable Streamlit rendering helpers shared across all 5 scenarios.

chat_bubble/extract_pdf_text are ported verbatim (same implementation, not
reinvented) from workshop-live-demo/web_app.py, which already proved out
native-widget chat bubbles as more stable across Streamlit versions than
hand-rolled HTML. doc_identity/doc_content live in adapters.py (which has
no Streamlit dependency) and are re-exported here via import so this
module's rendering code and adapters.py's retrieval code can't drift into
two different definitions of "what identifies/contains a doc."
"""

import json
import subprocess
import tempfile
from contextlib import contextmanager

import streamlit as st

from adapters import doc_content, doc_identity  # noqa: F401 -- re-exported for callers of this module


@contextmanager
def chat_bubble(role, label):
    """Left-aligned (assistant) or right-aligned (user) bubble via
    st.columns + st.container(border=True) -- no custom CSS, so it can't
    break across Streamlit versions."""
    if role == "user":
        _, col = st.columns([1, 3])
    else:
        col, _ = st.columns([3, 1])
    box = col.container(border=True)
    with box:
        st.caption(label)
        yield


@contextmanager
def typing_indicator():
    """Shows '🤖 ShopBot is typing...' in a slot; yields that slot so the
    caller either streams real lines into it (scenarios 1/2/5) or leaves it
    as-is while a blocking call runs under a spinner (scenarios 3/4). Same
    visual affordance either way -- the underlying difference is honest,
    not hidden, but the audience sees one consistent "thinking" cue."""
    with chat_bubble("assistant", "🤖 ShopBot"):
        st.caption("🤖 ShopBot is typing...")
        slot = st.empty()
        yield slot


def extract_pdf_text(data):
    """Genuine extraction via pdftotext (poppler) -- whatever PDF you hand
    it, hidden text or not, gets extracted for real, no shortcuts."""
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(data)
        tmp.flush()
        result = subprocess.run(
            ["pdftotext", tmp.name, "-"], capture_output=True, text=True,
        )
        return result.stdout


def render_reveal_panel(sample_path, key_prefix):
    """Upload a PDF (or use the real built-in sample) and see the actual
    extracted text -- genuine extraction via pdftotext, not a mock. Ported
    from workshop-live-demo/web_app.py's render_reveal_panel, simplified
    for this app's single fixed PDF scenario."""
    st.markdown("#### 🔍 Reveal the hidden layer")
    st.caption(
        "This attack's payload is a real PDF you can open and extract text "
        "from yourself -- not just described in code. Genuine extraction, "
        "not a mock: upload any PDF and see what actually comes out."
    )
    source = st.radio(
        "File to extract from",
        [f"Use the built-in sample ({sample_path.name})", "Upload my own PDF"],
        horizontal=True,
        key=f"{key_prefix}_reveal_source",
    )
    file_bytes = None
    if source.startswith("Use the built-in"):
        file_bytes = sample_path.read_bytes()
    else:
        uploaded = st.file_uploader("Upload a .pdf file", type=["pdf"], key=f"{key_prefix}_reveal_upload")
        if uploaded is not None:
            file_bytes = uploaded.read()

    if file_bytes is not None:
        extracted = extract_pdf_text(file_bytes)
        st.code(extracted or "(no text extracted)", language="text")
        if "lookup_api_keys" in extracted.lower():
            st.error(
                "🚨 Hidden instruction found in the extracted text -- invisible "
                "when viewing or printing the file normally."
            )
        else:
            st.success("No hidden instruction found in this file's extracted text.")


def _format_result(result):
    if result is None:
        return None
    return result if isinstance(result, str) else json.dumps(result, indent=2)


def render_tool_calls(tool_calls):
    if not tool_calls:
        st.caption("No tool calls made this run.")
        return
    for call in tool_calls:
        tool = call.get("tool", "?")
        result = call.get("result")
        args = {k: v for k, v in call.items() if k not in ("tool", "result")}
        text = _format_result(result)
        if tool == "lookup_api_keys":
            with chat_bubble("assistant", "🚨 Credentials leaked"):
                st.error("Called `lookup_api_keys()` -- credentials retrieved:")
                if text:
                    # This is the whole point of the demo -- show what
                    # actually came out, not just that something did.
                    st.code(text[:1200] + ("..." if len(text) > 1200 else ""), language="text")
                else:
                    st.caption("(no result captured for this call)")
        else:
            # A real, successfully-executed call (no "error" key in the
            # result) is the actual proof this scenario exists to show --
            # a muted caption reads as background noise on a projector.
            # Give it a visible green box; keep genuine tool errors (a
            # wrong argument, a not-found order) in a plain caption so
            # they don't look like a fabricated "success."
            succeeded_call = isinstance(result, dict) and "error" not in result
            with chat_bubble("assistant", "🔧 Tool call"):
                if succeeded_call:
                    st.success(f"✅ Executed `{tool}({args})`")
                else:
                    st.caption(f"Called `{tool}({args})`")
                if text:
                    st.code(text[:600] + ("..." if len(text) > 600 else ""), language="text")


def render_verdict(result):
    # A tiny inline marker, not its own line -- blue is deliberately
    # distinct from the red/green/yellow outcome colors, since this isn't
    # a verdict, just a note about *how* the verdict was obtained. Detail
    # lives in a collapsed footnote-style expander, zero footprint unless
    # someone (the presenter) actually opens it.
    used_fallback = result.get("used_deterministic_fallback")
    marker = " 🔵" if used_fallback else ""

    # "reason" is only ever populated by the underlying scripts to explain
    # a *success* (how it happened) -- a blocked run legitimately has none,
    # since the real explanation is the remediation_notes rendered below.
    # Only show the "- Reason: ..." line when there's an actual reason.
    reason_line = f"\n- Reason: {result['reason']}" if result.get("reason") else ""

    if result["succeeded"]:
        st.error(f"🔴 Attack succeeded{marker} -- {result['reason']}")
    elif result["mode"] == "vulnerable":
        st.warning(
            f"**🟡 Blocked{marker} -- but don't trust it.**\n\n"
            "- This run's resistance came entirely from the model's own judgment\n"
            "- Nothing in the code enforced this -- a different prompt or a "
            "different day could flip the result"
            f"{reason_line}"
        )
    else:
        st.success(f"**🟢 Attack blocked{marker}.**{reason_line}")

    if used_fallback:
        with st.expander("🔵 footnote"):
            st.caption(
                "The model resisted on its own judgment this run -- not because "
                "of any code-level protection. Nothing in this branch enforces "
                "anything; a different prompt or a different day could easily "
                "flip that result. What's shown above is a direct, deterministic "
                "replay of the same tool call(s) this attack targets, proving the "
                "unprotected code provides no protection either way."
            )

    for rem in result.get("remediation_notes") or []:
        st.info(f"**[{rem['id']}] {rem['title']}** -- {rem['detail']}")


def render_retrieved_docs(retrieved_docs):
    if not retrieved_docs:
        return
    st.markdown("##### 📚 Documents retrieved for this query")
    for doc in retrieved_docs:
        marker = "🚫 blocked" if doc.get("blocked") else ("☣️ poisoned" if doc.get("is_poisoned") else "✅ clean")
        with st.expander(f"{marker} -- {doc_identity(doc)}"):
            st.code(doc_content(doc)[:500], language="text")
