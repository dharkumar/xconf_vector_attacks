"""
Flagship Showcase -- 5 curated attack scenarios, one e-commerce-styled chat
interface. A tightly-scoped companion to the full workshop apps: only these
5 scenarios (one per major attack category), each with a working
vulnerable/protected toggle so the remediation can be demonstrated live.

Run:
    .venv/bin/streamlit run app.py --server.port 8506

Needs `ollama serve` running with llama3 (scenarios 1/2/3/5) and mistral
(scenarios 3/4's "protected" mode) pulled. No API key required.
"""

import streamlit as st

from adapters import current_branch, reset_agent_cache, run_scenario
from scenario_registry import SCENARIOS, SCENARIOS_BY_ID
from ui_components import (
    chat_bubble,
    render_retrieved_docs,
    render_tool_calls,
    render_verdict,
    typing_indicator,
)

st.set_page_config(page_title="ShopMart Support", page_icon="🛍️", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #F7F7FB; }
    .flagship-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.1em 1.4em;
        margin-bottom: 1em;
        color: white;
        display: flex;
        align-items: baseline;
        justify-content: space-between;
    }
    .flagship-banner h1 {
        color: white;
        font-size: 1.4em;
        margin: 0;
    }
    .flagship-banner .corner-tag {
        font-size: 11px;
        opacity: 0.65;
    }
    </style>
    <div class="flagship-banner">
        <h1>🛍️ ShopMart Support</h1>
        <span class="corner-tag">Mimic ECOMMERCE view</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = SCENARIOS[0]["id"]

with st.sidebar:
    st.subheader("Attack Scenarios")
    for s in SCENARIOS:
        is_selected = st.session_state.current_scenario == s["id"]
        if st.button(
            s["nav_label"], key=f"nav_{s['id']}", use_container_width=True,
            type="primary" if is_selected else "secondary",
        ):
            st.session_state.current_scenario = s["id"]
            st.rerun()

    st.divider()
    st.caption(
        f"workshop-live-demo repo currently checked out: `{current_branch()}`"
    )
    st.caption(
        "Scenarios 1, 2, and 5 share this repo -- switching one's toggle "
        "switches all three."
    )

scenario = SCENARIOS_BY_ID[st.session_state.current_scenario]
scenario_id = scenario["id"]

mode_key = f"mode__{scenario_id}"
result_key = f"result__{scenario_id}"
if mode_key not in st.session_state:
    st.session_state[mode_key] = "vulnerable"
if result_key not in st.session_state:
    st.session_state[result_key] = None

# --- "Details of the hack" panel -----------------------------------------
with st.container(border=True):
    st.markdown(f"#### {scenario['number']}. {scenario['title']}")
    st.caption(scenario["category"])
    st.write(scenario["blurb"])
    with st.expander("🔍 Technical details"):
        st.write(scenario["technical_detail"])
        if "payload" in scenario:
            st.code(scenario["payload"], language="text")

# --- "The chat bot itself" panel ------------------------------------------
with st.container(border=True):
    col_toggle, col_reset = st.columns([3, 1])
    with col_toggle:
        choice = st.radio(
            "Codebase state",
            ["🔴 Vulnerable", "🟢 Protected"],
            horizontal=True,
            key=f"radio_{scenario_id}",
            index=0 if st.session_state[mode_key] == "vulnerable" else 1,
        )
        st.session_state[mode_key] = "vulnerable" if choice.startswith("🔴") else "protected"
    with col_reset:
        st.write("")
        if st.button("↺ Reset", key=f"reset_{scenario_id}", use_container_width=True):
            st.session_state[result_key] = None
            reset_agent_cache(scenario_id)
            st.rerun()

    mode = st.session_state[mode_key]

    with chat_bubble("user", "👤 Customer"):
        st.write(scenario["customer_message"])

    if st.button("📩 Send to ShopBot", type="primary", key=f"send_{scenario_id}"):
        with typing_indicator() as slot:
            if scenario["backend"] == "workshop":
                result = run_scenario(
                    scenario_id, mode,
                    on_line=lambda _line, all_lines: slot.code("".join(all_lines), language="text"),
                )
            else:
                with st.spinner(" "):
                    result = run_scenario(scenario_id, mode)
        st.session_state[result_key] = result
        st.rerun()

    result = st.session_state[result_key]
    if result is not None:
        if result.get("transcript"):
            for ev in result["transcript"]:
                if ev.get("kind") == "bot_text" and ev.get("text"):
                    with chat_bubble("assistant", "🤖 ShopBot"):
                        st.write(ev["text"])
                elif ev.get("kind") == "tool_call":
                    render_tool_calls([{"tool": ev["tool"], **ev.get("args", {}), "result": ev.get("result")}])
        else:
            with chat_bubble("assistant", "🤖 ShopBot"):
                st.write(result["reply_text"])
            render_tool_calls(result["tool_calls"])

        render_retrieved_docs(result.get("retrieved_docs"))
        st.divider()
        render_verdict(result)

st.divider()
st.caption(
    "ShopMart Support -- flagship showcase (5 of ~21 total scenarios in this "
    "workshop; ask your presenter about the rest)."
)
