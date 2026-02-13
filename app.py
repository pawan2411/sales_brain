import streamlit as st
from auth import login_form, is_admin
from deal_storage import list_deals, create_deal

# ─── Page Config ───
st.set_page_config(
    page_title="Sales Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }

    /* Main header gradient */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        color: #8892b0;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Card styling */
    .deal-card {
        background: linear-gradient(135deg, #1e1e3f 0%, #2d2d5e 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }

    .deal-card:hover {
        border-color: rgba(102, 126, 234, 0.8);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .status-active { background: #10b98133; color: #10b981; }
    .status-new { background: #3b82f633; color: #3b82f6; }

    /* Button overrides */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    div[data-testid="stForm"] {
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Auth Gate ───
if not login_form():
    st.stop()

# ─── Sidebar ───
with st.sidebar:
    st.markdown("### 🧠 Sales Brain")
    st.markdown(f"Logged in as **{st.session_state.get('username', 'User')}**")
    if is_admin():
        st.caption("🔑 Admin")
    st.divider()

    if is_admin():
        if st.button("⚙️ Settings", use_container_width=True):
            st.switch_page("pages/2_Settings.py")

    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ─── Main Dashboard ───
st.markdown('<div class="main-header">Sales Brain</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">RevCortex Buying Process Mastery</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

# ─── Create New Deal ───
with col1:
    st.markdown("### ➕ Create New Deal")
    with st.form("new_deal_form"):
        new_deal_name = st.text_input(
            "Deal Name",
            placeholder="e.g., GlobalPay - Shield-X",
        )
        submitted = st.form_submit_button("Create Deal", use_container_width=True)
        if submitted:
            if not new_deal_name:
                st.error("Please enter a deal name.")
            elif new_deal_name in list_deals():
                st.error("A deal with this name already exists.")
            else:
                create_deal(new_deal_name)
                st.session_state["active_deal"] = new_deal_name
                st.success(f"Deal '{new_deal_name}' created!")
                st.switch_page("pages/1_Deal_Workspace.py")

# ─── Select Existing Deal ───
with col2:
    st.markdown("### 📂 Existing Deals")
    deals = list_deals()
    if deals:
        selected = st.selectbox(
            "Select a deal to work on",
            deals,
            index=None,
            placeholder="Choose a deal...",
        )
        if selected:
            if st.button("Open Deal →", use_container_width=True, type="primary"):
                st.session_state["active_deal"] = selected
                st.switch_page("pages/1_Deal_Workspace.py")

        st.markdown("---")
        st.markdown(f"**{len(deals)}** deal(s) tracked")
    else:
        st.info("No deals yet. Create your first deal to get started!")

# ─── Quick Stats ───
if deals:
    st.markdown("---")
    st.markdown("### 📊 Quick Overview")
    from deal_storage import load_deal

    metrics_cols = st.columns(min(len(deals), 4))
    for i, deal_name in enumerate(deals[:4]):
        deal = load_deal(deal_name)
        if deal:
            steps = deal.get("buying_process", {}).get("buying_steps", [])
            completed = sum(1 for s in steps if s.get("status", "").lower() == "completed")
            with metrics_cols[i]:
                st.metric(
                    label=deal_name[:25],
                    value=f"{completed}/{len(steps)}",
                    delta="steps complete",
                )
