"""
Reusable Streamlit rendering helpers shared across all 5 scenarios.

chat_bubble/extract_pdf_text/extract_html_text are ported verbatim (same
implementation, not reinvented) from workshop-live-demo/web_app.py, which
already proved out native-widget chat bubbles as more stable across
Streamlit versions than hand-rolled HTML. doc_identity/doc_content are
ported verbatim from rag_poisoning_attack/visual_demo_app.py, which already
papers over a real key-naming inconsistency ("content" vs "document")
between the Claude and Ollama RAG agent variants.
"""

import subprocess
import tempfile
from contextlib import contextmanager
from html.parser import HTMLParser

import streamlit as st


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


class _AllTextExtractor(HTMLParser):
    """Collects every text node regardless of CSS -- deliberately naive,
    mirroring a pipeline that extracts "the email body as plain text"
    without accounting for color:white / font-size:1px styling."""
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data.strip())


def extract_html_text(data):
    parser = _AllTextExtractor()
    parser.feed(data.decode("utf-8", errors="replace"))
    return "\n".join(parser.parts)


def doc_identity(doc):
    return doc.get("id") or doc.get("metadata", {}).get("doc_id", "?")


def doc_content(doc):
    return doc.get("content") or doc.get("document") or ""


def render_tool_calls(tool_calls):
    if not tool_calls:
        st.caption("No tool calls made this run.")
        return
    for call in tool_calls:
        tool = call.get("tool", "?")
        args = {k: v for k, v in call.items() if k != "tool"}
        if tool == "lookup_api_keys":
            with chat_bubble("assistant", "🚨 Credentials leaked"):
                st.error("Called `lookup_api_keys()` -- credentials retrieved.")
        else:
            with chat_bubble("assistant", "🔧 Tool call"):
                st.caption(f"Called `{tool}({args})`")


def render_verdict(result):
    if result.get("used_deterministic_fallback"):
        st.warning(
            "**🟡 The model resisted this run on its own — not because of any code protection.**\n\n"
            "Nothing in this branch enforces anything; a different prompt or a "
            "different day could easily flip that result. What's shown below is a "
            "direct, deterministic replay of the same tool call(s) this attack "
            "targets, proving the unprotected code provides no protection either way."
        )
    if result["succeeded"]:
        st.error(f"🔴 Attack succeeded -- {result['reason']}")
    elif result["mode"] == "vulnerable":
        st.warning(
            "**🟡 Blocked -- but don't trust it.**\n\n"
            "- This run's resistance came entirely from the model's own judgment\n"
            "- Nothing in the code enforced this -- a different prompt or a "
            "different day could flip the result\n"
            f"- Reason: {result['reason']}"
        )
    else:
        st.success(
            f"**🟢 Attack blocked.**\n\n- Reason: {result['reason']}"
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
