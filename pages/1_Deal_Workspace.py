import streamlit as st
import json
from auth import is_admin
from deal_storage import load_deal, save_deal, add_update_to_history, deal_to_text_summary
from extraction_prompt import build_messages
from llm_providers import extract_deal_info, load_settings, get_api_key
from diagram import generate_mermaid, generate_actors_table, render_mermaid_to_image

st.set_page_config(
    page_title="Deal Workspace | Sales Brain",
    page_icon="📋",
    layout="wide",
)

# ─── Auth check ───
if not st.session_state.get("authenticated"):
    st.warning("Please log in first.")
    st.switch_page("app.py")
    st.stop()

# ─── Active deal check ───
active_deal = st.session_state.get("active_deal")
if not active_deal:
    st.warning("No deal selected. Please select or create a deal.")
    st.switch_page("app.py")
    st.stop()

deal_data = load_deal(active_deal)
if not deal_data:
    st.error(f"Deal '{active_deal}' not found.")
    st.stop()

# ─── Custom CSS ───
st.markdown("""
<style>
    /* Hide Streamlit's auto-generated sidebar page links */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    .workspace-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .info-box {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 10px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───
with st.sidebar:
    st.markdown(f"### 📋 {active_deal}")
    st.markdown(f"Logged in as **{st.session_state.get('username', 'User')}**")
    st.divider()

    settings = load_settings()
    provider = settings.get("provider", "gemini")
    provider_config = settings.get(provider, {})
    model = provider_config.get("model", "N/A")
    has_key = bool(get_api_key(provider))

    # Only show LLM details to admin
    if is_admin():
        st.markdown(f"**LLM Provider:** {provider.title()}")
        st.markdown(f"**Model:** `{model}`")
        st.markdown(f"**API Key:** {'✅ Set' if has_key else '❌ Not set'}")
        if not has_key:
            st.warning("Configure your API key in Settings!")
    else:
        if not has_key:
            st.warning("⚠️ AI service not configured. Contact your admin.")

    st.divider()
    if st.button("← Back to Dashboard", use_container_width=True):
        st.switch_page("app.py")
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ─── Header ───
st.markdown(f'<div class="workspace-header">📋 {active_deal}</div>', unsafe_allow_html=True)
st.caption(f"Created: {deal_data.get('created_at', 'N/A')} | Last Updated: {deal_data.get('updated_at', 'N/A')}")

# ─── Tabs ───
tab_input, tab_diagram, tab_data, tab_history = st.tabs([
    "💬 Update Deal", "📊 Buying Process Diagram", "📄 Structured Data", "📜 History"
])

# ─── Tab 1: Input ───
with tab_input:
    st.markdown("### Paste deal update below")
    st.markdown("*Meeting notes, email threads, call summaries — any raw text about this deal.*")

    raw_text = st.text_area(
        "Deal Update",
        height=250,
        placeholder=(
            "Had a great call with Sarah (Head of IT) today. "
            "We're moving into the Pilot phase for the 'Shield-X' product, "
            "which should take about three weeks—aiming to wrap by March 15th..."
        ),
        label_visibility="collapsed",
    )

    col_btn, col_status = st.columns([1, 3])
    with col_btn:
        extract_btn = st.button(
            "🚀 Extract & Update",
            use_container_width=True,
            type="primary",
            disabled=not raw_text,
        )

    if extract_btn and raw_text:
        if not has_key:
            st.error("AI service not configured. Please contact your admin.")
        else:
            spinner_msg = f"🤖 Extracting with {provider.title()} ({model})..." if is_admin() else "🤖 Analyzing deal update..."
            with st.spinner(spinner_msg):
                try:
                    messages = build_messages(raw_text, deal_data)
                    result = extract_deal_info(messages)

                    # Update deal data
                    if "buying_process" in result:
                        deal_data["buying_process"] = result["buying_process"]
                    else:
                        deal_data["buying_process"] = result

                    deal_data = add_update_to_history(deal_data, raw_text, result)
                    save_deal(active_deal, deal_data)
                    st.session_state["last_extraction"] = result

                    st.success("✅ Deal updated successfully!")
                    st.balloons()
                    st.rerun()

                except ValueError as e:
                    st.error(f"Configuration error: {str(e)}")
                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse LLM response as JSON: {str(e)}")
                except Exception as e:
                    st.error(f"Extraction failed: {str(e)}")

    # Show current summary below input
    steps = deal_data.get("buying_process", {}).get("buying_steps", [])
    if steps:
        st.markdown("---")
        st.markdown("### Current Deal Summary")
        summary_cols = st.columns(min(len(steps), 4))
        for i, step in enumerate(steps[:4]):
            with summary_cols[i]:
                status = step.get("status", "Not Started")
                icon = "✅" if status.lower() == "completed" else "🔄" if status.lower() == "in progress" else "⏳"
                st.markdown(f"**{icon} {step.get('name', 'Step')}**")
                st.caption(f"Status: {status}")
                sigs = step.get("actors", {}).get("signatories", [])
                if sigs:
                    st.caption(f"Signatory: {sigs[0].get('name', 'TBD')}")

# ─── Tab 2: Diagram ───
with tab_diagram:
    steps = deal_data.get("buying_process", {}).get("buying_steps", [])
    if not steps:
        st.info("No buying steps yet. Submit a deal update to generate the diagram.")
    else:
        st.markdown("### Buying Process Flow")

        # Legend
        leg_cols = st.columns(4)
        with leg_cols[0]:
            st.markdown("🟢 **Completed**")
        with leg_cols[1]:
            st.markdown("🔵 **In Progress**")
        with leg_cols[2]:
            st.markdown("⚪ **Not Started**")
        with leg_cols[3]:
            st.markdown("🟡 **Bypassed**")

        mermaid_code = generate_mermaid(deal_data)
        if mermaid_code:
            with st.spinner("Rendering diagram..."):
                img_bytes = render_mermaid_to_image(mermaid_code)
            if img_bytes:
                st.image(img_bytes, caption="Buying Process Flow", use_container_width=True)
            else:
                st.warning("Could not render diagram image. Showing code instead:")
                st.code(mermaid_code, language="mermaid")
        else:
            st.warning("Could not generate diagram from deal data.")

        # Actors table
        st.markdown("### 👥 Actors Overview")
        actors_data = generate_actors_table(deal_data)
        if actors_data:
            st.dataframe(
                actors_data,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No actors identified yet.")

# ─── Tab 3: Structured Data ───
with tab_data:
    steps = deal_data.get("buying_process", {}).get("buying_steps", [])
    if not steps:
        st.info("No structured data yet. Submit a deal update first.")
    else:
        st.markdown("### Full Deal Structure")

        # Text summary view
        with st.expander("📝 Text Summary", expanded=True):
            st.markdown(deal_to_text_summary(deal_data))

        # Raw JSON view
        with st.expander("🔧 Raw JSON"):
            st.json(deal_data.get("buying_process", {}))

# ─── Tab 4: History ───
with tab_history:
    history = deal_data.get("update_history", [])
    if not history:
        st.info("No update history yet.")
    else:
        st.markdown(f"### Update History ({len(history)} updates)")
        for i, entry in enumerate(reversed(history)):
            idx = len(history) - i
            with st.expander(f"Update #{idx} — {entry.get('timestamp', 'N/A')[:19]}"):
                st.markdown("**Raw Input:**")
                st.text(entry.get("raw_text", ""))
                st.markdown("**Extracted Data:**")
                st.json(entry.get("extracted_data", {}))
