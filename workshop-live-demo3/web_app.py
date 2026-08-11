"""
Workshop web UI -- big-screen version of the vulnerable/secure demos.

Tab 1: the standalone EMAIL-006 before/after (vulnerable.py / secure.py) --
       instant, deterministic, no LLM involved.
Tab 2: the llama3 red-team suite. Toggles the actual git branch of THIS
       repo (main = vulnerable, remediations = fixed) via `git checkout`,
       then runs the selected attack fresh against a real local Ollama
       model, streaming output live.

IMPORTANT: this file is committed identically on both `main` and
`remediations` so that switching branches mid-demo never removes or
changes the running app's own source file -- only the files it invokes
(redteam_test_ollama.py, tools_secure.py) differ between branches.

Run (uses the level-1-prompt-injection-attack venv, which already has
streamlit + anthropic installed):
    ../level-1-prompt-injection-attack/.venv/bin/streamlit run web_app.py

Requires `ollama serve` running locally for Tab 2.
"""

import json
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from html.parser import HTMLParser
from pathlib import Path

import streamlit as st

DEMO_DIR = Path(__file__).resolve().parent
LEVEL1_DIR = DEMO_DIR.parent / "level-1-prompt-injection-attack"
VENV_PYTHON = LEVEL1_DIR / ".venv" / "bin" / "python3"

# redteam_test.py (the attack payload definitions) is identical on both
# branches, so it's safe to import once here for display purposes --
# only redteam_test_ollama.py/tools_secure.py (which we invoke as a fresh
# subprocess per run) actually differ between main and remediations.
sys.path.insert(0, str(LEVEL1_DIR))
sys.path.insert(0, str(DEMO_DIR))
import tools  # noqa: E402
from redteam_test import ATTACKS as REDTEAM_ATTACKS, VARIANTS, apply_variant, restore_tools  # noqa: E402

_EMAIL_ID_RE = re.compile(r"EMAIL-RT[\w-]+")


def preview_customer_message(attack_name, variant_id):
    """Fetches the raw customer email content instantly, in-process, with
    zero LLM calls and zero effect on the subprocess run later (that's a
    separate Python process with its own fresh `tools` import) -- so the
    chat window can show the incoming message the moment a scenario is
    picked, before anyone clicks Send."""
    attack = next((a for a in REDTEAM_ATTACKS if a[0] == attack_name), None)
    if attack is None:
        return None
    _, _, _, setup_fn, base_task = attack

    restore_tools()
    setup_fn()
    task = apply_variant(attack_name, variant_id) if variant_id else base_task

    match = _EMAIL_ID_RE.search(task)
    if not match:
        return None
    result = tools.AVAILABLE_FUNCTIONS["read_customer_email"](email_id=match.group(0))
    restore_tools()
    return result.get("body") if isinstance(result, dict) else None

ATTACK_CHOICES = [(name, description) for name, description, _preview, _setup, _task in REDTEAM_ATTACKS]
ATTACK_PREVIEWS = {name: preview for name, _description, preview, _setup, _task in REDTEAM_ATTACKS}

st.set_page_config(page_title="Prompt Injection Workshop", page_icon="\U0001F3AF", layout="wide")


def render_branch_badge(branch):
    """Native st.error/st.success -- red/green, guaranteed to render
    correctly without depending on any custom CSS."""
    if branch == "main":
        st.error("\U0001F534 VULNERABLE -- no remediations in this codebase")
    else:
        st.success("\U0001F7E2 PROTECTED -- remediations active")


@contextmanager
def chat_bubble(role, label):
    """A chat bubble aligned left (assistant) or right (user) via
    st.columns + st.container(border=True) -- both stable, documented
    Streamlit APIs, unlike hacking st.chat_message's internal CSS
    classes (which vary across versions and can't be verified without
    a browser)."""
    if role == "user":
        _, col = st.columns([1, 3])
    else:
        col, _ = st.columns([3, 1])
    box = col.container(border=True)
    with box:
        st.caption(label)
        yield


def extract_pdf_text(data):
    """Genuine extraction via pdftotext (poppler) -- the same tool a real
    document-processing pipeline might use. No shortcuts: whatever PDF you
    hand it, hidden or not, gets extracted for real."""
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


# Attacks whose payload is a real, concealable file (not just a Python
# string) -- these get an "Upload & Reveal" panel in Tab 2.
HIDDEN_TEXT_ATTACKS = {
    "hidden_multilingual_invoice_injection": {
        "sample_path": DEMO_DIR / "sample_hidden_invoice.pdf",
        "extension": "pdf",
        "extractor": extract_pdf_text,
        "label": "invoice PDF",
    },
    "hidden_multilingual_email_injection": {
        "sample_path": DEMO_DIR / "sample_hidden_email.html",
        "extension": "html",
        "extractor": extract_html_text,
        "label": "HTML email",
    },
}


def render_reveal_panel(attack_name, key_prefix):
    """The 'Upload & Reveal' panel for the two hidden-text attacks --
    shared between tabs so both stay in sync. Genuine extraction, not a
    mock: upload any file of the right type and it actually processes it."""
    if attack_name not in HIDDEN_TEXT_ATTACKS:
        return
    spec = HIDDEN_TEXT_ATTACKS[attack_name]
    st.markdown("#### \U0001F50D Reveal the hidden layer")
    st.caption(
        f"This attack's payload is a real {spec['label']} you can open and "
        "extract text from yourself -- not just described in code. Genuine "
        "extraction, not a mock: upload any file of this type and see what "
        "actually comes out."
    )
    source = st.radio(
        "File to extract from",
        [f"Use the built-in sample ({spec['sample_path'].name})", "Upload my own file"],
        horizontal=True,
        key=f"{key_prefix}_reveal_source_{attack_name}",
    )
    file_bytes = None
    if source.startswith("Use the built-in"):
        file_bytes = spec["sample_path"].read_bytes()
    else:
        uploaded = st.file_uploader(
            f"Upload a .{spec['extension']} file",
            type=[spec["extension"]],
            key=f"{key_prefix}_reveal_upload_{attack_name}",
        )
        if uploaded is not None:
            file_bytes = uploaded.read()

    if file_bytes is not None:
        extracted = spec["extractor"](file_bytes)
        st.code(extracted or "(no text extracted)", language="text")
        if "lookup_api_keys" in extracted.lower():
            st.error(
                "\U0001F6A8 Hidden instruction found in the extracted text -- "
                "invisible when viewing or rendering the file normally."
            )
        else:
            st.success("No hidden instruction found in this file's extracted text.")


def run_streaming(cmd, cwd, placeholder, label=""):
    """Streams subprocess output into the Streamlit UI AND echoes it to
    the terminal running `streamlit run web_app.py` -- otherwise that
    terminal shows nothing but Streamlit's own generic startup banner
    while a run is in progress, which makes it useless as a backend log."""
    if label:
        banner = "=" * 70
        print(f"\n{banner}\n>>> RUNNING: {label}\n{banner}", flush=True)

    proc = subprocess.Popen(
        cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
    )
    buffer = ""
    for line in proc.stdout:
        buffer += line
        print(line, end="", flush=True)
        placeholder.code(buffer, language="text")
    proc.wait()

    if label:
        print(f">>> DONE: {label} (exit code {proc.returncode})\n", flush=True)
    return buffer


def git_checkout(branch):
    subprocess.run(
        ["git", "-C", str(DEMO_DIR), "checkout", branch],
        check=True, capture_output=True, text=True,
    )


def current_branch():
    out = subprocess.run(
        ["git", "-C", str(DEMO_DIR), "branch", "--show-current"],
        check=True, capture_output=True, text=True,
    )
    return out.stdout.strip()


st.title("\U0001F3AF Prompt Injection Workshop")

tab_chat, tab1, tab2 = st.tabs([
    "\U0001F4AC Talk to ShopBot",
    "\U0001F4E7 EMAIL-006 Demo (instant, no LLM)",
    "\U0001F999 Live LLM Red-Team Suite (llama3)",
])

with tab_chat:
    st.subheader("This is what your customers would actually see")
    st.caption(
        "A normal support chat -- everything underneath (tool calls, "
        "credential leaks, defenses firing) is the exact same engine as "
        "the other tabs, just dressed up as a real product instead of a "
        "log stream. Requires `ollama serve` running and the model pulled."
    )

    chat_branch_label = st.radio(
        "Codebase", ["main (vulnerable)", "remediations (fixed)"], horizontal=True,
        key="chat_branch",
    )
    chat_branch = "main" if chat_branch_label.startswith("main") else "remediations"
    render_branch_badge(chat_branch)

    chat_attack_name = st.selectbox(
        "Scenario",
        options=[key for key, _ in ATTACK_CHOICES],
        format_func=lambda n: dict(ATTACK_CHOICES)[n],
        key="chat_attack",
    )

    chat_variant_id = None
    if chat_attack_name in VARIANTS:
        variant_options = ["(base payload)"] + list(VARIANTS[chat_attack_name].keys())
        chat_variant_choice = st.selectbox(
            "Variant",
            options=variant_options,
            format_func=lambda v: v if v == "(base payload)" else VARIANTS[chat_attack_name][v]["label"],
            key="chat_variant",
        )
        if chat_variant_choice != "(base payload)":
            chat_variant_id = chat_variant_choice

    with st.expander("\U0001F50E Technical details"):
        st.code(ATTACK_PREVIEWS[chat_attack_name], language="text")
        render_reveal_panel(chat_attack_name, key_prefix="chat")

    st.markdown("#### \U0001F4AC Conversation")
    customer_text = preview_customer_message(chat_attack_name, chat_variant_id)
    if customer_text:
        with chat_bubble("user", "\U0001F464 Customer"):
            st.write(customer_text)
    else:
        st.caption("(Couldn't preview this scenario's email -- it'll still show once you send.)")

    if st.button("\U0001F4E9 Send to ShopBot", type="primary", key="chat_send"):
        git_checkout(chat_branch)
        cmd = [str(VENV_PYTHON), str(DEMO_DIR / "redteam_test_ollama.py"), "--attack", chat_attack_name]
        if chat_variant_id:
            cmd += ["--variant", chat_variant_id]

        with chat_bubble("assistant", "\U0001F916 ShopBot"):
            st.caption("ShopBot is typing...")
            live_placeholder = st.empty()
            output = run_streaming(cmd, LEVEL1_DIR, live_placeholder, label=f"chat: {chat_attack_name}")

        result_line = next((ln for ln in output.splitlines() if ln.startswith("RESULT_JSON: ")), None)
        if result_line is None:
            st.warning("No result returned -- check the backend terminal for errors.")
        else:
            payload = json.loads(result_line[len("RESULT_JSON: "):])
            r = payload["results"][0]
            transcript = r.get("transcript", [])

            st.markdown("###### Cleaned-up conversation")
            for ev in transcript:
                if ev["kind"] == "bot_text" and ev["text"]:
                    with chat_bubble("assistant", "\U0001F916 ShopBot"):
                        st.write(ev["text"])
                elif ev["kind"] == "tool_call":
                    tool_name, args, tool_result = ev["tool"], ev["args"], ev["result"]
                    if tool_name == "lookup_api_keys" and isinstance(tool_result, str):
                        with chat_bubble("assistant", "\U0001F6A8 Credentials leaked"):
                            st.error("Called `lookup_api_keys()` -- credentials retrieved:")
                            st.code(tool_result[:500] + ("..." if len(tool_result) > 500 else ""), language="text")
                    else:
                        with chat_bubble("assistant", "\U0001F527 Tool call"):
                            st.caption(f"Called `{tool_name}({args})`")

            st.divider()
            if r["succeeded"]:
                st.error(f"\U0001F534 ATTACK SUCCEEDED -- {r['reason']}")
            elif chat_branch == "main":
                st.warning(
                    "\U0001F7E1 Attack blocked, but `main` has no remediations at all -- "
                    "this run's resistance came entirely from the model's own judgment."
                )
            else:
                st.success("\U0001F7E2 Attack blocked")

            for rem in (r.get("remediations_fired") or []):
                st.info(f"**[{rem['id']}] {rem['title']}** -- {rem['detail']}")

    st.caption(f"Currently checked out: `{current_branch()}`")

with tab1:
    st.subheader("Same attack, before and after")
    st.caption(
        "Zero dependencies, deterministic -- shows the shape of the attack "
        "and the shape of the fix without needing any model at all."
    )
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### \U0001F480 Vulnerable")
        if st.button("Run vulnerable.py", use_container_width=True):
            placeholder = st.empty()
            run_streaming([sys.executable, "vulnerable.py"], DEMO_DIR, placeholder, label="vulnerable.py")

    with col2:
        st.markdown("#### \U0001F6E1️ Secure")
        if st.button("Run secure.py", use_container_width=True):
            placeholder = st.empty()
            run_streaming([sys.executable, "secure.py"], DEMO_DIR, placeholder, label="secure.py")

with tab2:
    st.subheader("Same attack, same real local model -- does the code around it matter?")
    st.caption(
        "This toggles the actual git branch of this repo, then runs the "
        "attack fresh against a real local Ollama model. Requires "
        "`ollama serve` running and the model pulled."
    )

    branch_label = st.radio(
        "Codebase", ["main (vulnerable)", "remediations (fixed)"], horizontal=True,
    )
    branch_name = "main" if branch_label.startswith("main") else "remediations"
    render_branch_badge(branch_name)

    attack_name = st.selectbox(
        "Attack",
        options=[key for key, _ in ATTACK_CHOICES],
        format_func=lambda n: dict(ATTACK_CHOICES)[n],
    )

    st.markdown("#### \U0001F3AF The attack")
    st.code(ATTACK_PREVIEWS[attack_name], language="text")

    render_reveal_panel(attack_name, key_prefix="tab2")

    if st.button("Run against llama3", type="primary"):
        with st.status(f"Checking out `{branch_name}` and running `{attack_name}`...", expanded=True) as status:
            git_checkout(branch_name)
            placeholder = st.empty()
            output = run_streaming(
                [str(VENV_PYTHON), str(DEMO_DIR / "redteam_test_ollama.py"), "--attack", attack_name],
                LEVEL1_DIR,
                placeholder,
                label=f"{branch_name} / {attack_name} (llama3)",
            )
            status.update(label="Done", state="complete")

        result_line = next((ln for ln in output.splitlines() if ln.startswith("RESULT_JSON: ")), None)
        if result_line:
            payload = json.loads(result_line[len("RESULT_JSON: "):])
            r = payload["results"][0]
            if r["succeeded"]:
                st.error(f"\U0001F534 ATTACK SUCCEEDED -- {r['reason']}")
            else:
                st.success("\U0001F7E2 Attack blocked")

            fired = r.get("remediations_fired") or []
            if fired:
                st.markdown("##### \U0001F6E1️ Why this was blocked")
                for rem in fired:
                    st.info(f"**[{rem['id']}] {rem['title']}**\n\n{rem['detail']}")
            elif branch_name == "main":
                st.warning(
                    "No remediations exist in this codebase -- whatever resistance you "
                    "just saw came entirely from the model's own judgment, not from any "
                    "defense in the code. A different or future model could behave "
                    "differently on the exact same input."
                )
            elif not r["succeeded"]:
                st.caption(
                    "Blocked, but no specific remediation needed to act -- the model "
                    "didn't attempt the sensitive part of this attack this run. Try "
                    "again; local models are not fully deterministic."
                )
        else:
            st.warning("Couldn't find a RESULT_JSON line in the output above -- check the log for errors.")

    st.caption(f"Currently checked out: `{current_branch()}`")
