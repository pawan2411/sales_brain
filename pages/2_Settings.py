import streamlit as st
from llm_providers import load_settings, save_settings, test_connection, get_api_key, set_api_key
from auth import is_admin

st.set_page_config(
    page_title="Settings | Sales Brain",
    page_icon="⚙️",
    layout="wide",
)

# ─── Auth check ───
if not st.session_state.get("authenticated"):
    st.warning("Please log in first.")
    st.switch_page("app.py")
    st.stop()

# ─── Admin check ───
if not is_admin():
    st.error("⛔ Settings are only accessible to the admin.")
    st.switch_page("app.py")
    st.stop()

# ─── Custom CSS ───
st.markdown("""
<style>
    /* Hide Streamlit's auto-generated sidebar page links */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    .settings-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.8rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown(f"Logged in as **{st.session_state.get('username', 'User')}**")
    st.divider()
    if st.button("← Back to Dashboard", use_container_width=True):
        st.switch_page("app.py")
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ─── Header ───
st.markdown('<div class="settings-header">⚙️ Settings</div>', unsafe_allow_html=True)
st.caption("Configure your LLM provider, API keys, and model preferences")

st.info("🔒 **API keys are session-only** — they stay in memory and are never saved to disk. You'll need to re-enter them each time you restart the app.", icon="🔐")

settings = load_settings()

# ─── Provider Selection ───
st.markdown("### 🤖 LLM Provider")

provider_options = {
    "gemini": "🔷 Google Gemini",
    "together": "🟣 Together AI (Qwen)",
    "deepseek": "🔵 DeepSeek",
}

current_provider = settings.get("provider", "gemini")
selected_provider = st.radio(
    "Select your LLM provider",
    options=list(provider_options.keys()),
    format_func=lambda x: provider_options[x],
    index=list(provider_options.keys()).index(current_provider),
    horizontal=True,
)

st.markdown("---")

# ─── Provider Configs ───
st.markdown("### 🔑 API Configuration")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🔷 Gemini")
    is_active = selected_provider == "gemini"
    if is_active:
        st.success("✅ Active provider")

    gemini_key = st.text_input(
        "Gemini API Key",
        value=get_api_key("gemini"),
        type="password",
        key="gemini_key_input",
        help="Get your key from https://aistudio.google.com/apikey\n\n🔒 Session-only, never saved to disk.",
    )
    gemini_model = st.text_input(
        "Gemini Model",
        value=settings.get("gemini", {}).get("model", "gemini-2.5-flash"),
        key="gemini_model",
        help="e.g. gemini-2.5-flash, gemini-2.5-pro",
    )

with col2:
    st.markdown("#### 🟣 Together AI")
    is_active = selected_provider == "together"
    if is_active:
        st.success("✅ Active provider")

    together_key = st.text_input(
        "Together API Key",
        value=get_api_key("together"),
        type="password",
        key="together_key_input",
        help="Get your key from https://api.together.xyz/settings/api-keys\n\n🔒 Session-only, never saved to disk.",
    )
    together_model = st.text_input(
        "Together Model",
        value=settings.get("together", {}).get("model", "Qwen/Qwen3-Next-80B-A3B-Instruct"),
        key="together_model",
        help="e.g. Qwen/Qwen3-Next-80B-A3B-Instruct",
    )

with col3:
    st.markdown("#### 🔵 DeepSeek")
    is_active = selected_provider == "deepseek"
    if is_active:
        st.success("✅ Active provider")

    deepseek_key = st.text_input(
        "DeepSeek API Key",
        value=get_api_key("deepseek"),
        type="password",
        key="deepseek_key_input",
        help="Get your key from https://platform.deepseek.com/api_keys\n\n🔒 Session-only, never saved to disk.",
    )
    deepseek_model = st.text_input(
        "DeepSeek Model",
        value=settings.get("deepseek", {}).get("model", "deepseek-chat"),
        key="deepseek_model",
        help="e.g. deepseek-chat, deepseek-reasoner",
    )

st.markdown("---")

# ─── Save & Test ───
save_col, test_col = st.columns(2)

with save_col:
    if st.button("💾 Save Settings", use_container_width=True, type="primary"):
        # Save provider & model preferences to disk (NO API keys)
        new_settings = {
            "provider": selected_provider,
            "gemini": {"model": gemini_model},
            "together": {"model": together_model},
            "deepseek": {"model": deepseek_model},
        }
        save_settings(new_settings)

        # Store API keys in session state only
        set_api_key("gemini", gemini_key)
        set_api_key("together", together_key)
        set_api_key("deepseek", deepseek_key)

        st.success("✅ Settings saved! (API keys in session only)")
        st.rerun()

with test_col:
    if st.button("🔗 Test Connection", use_container_width=True):
        # Temporarily store keys in session for the test
        set_api_key("gemini", gemini_key)
        set_api_key("together", together_key)
        set_api_key("deepseek", deepseek_key)

        # Also save provider/model in case changed
        new_settings = {
            "provider": selected_provider,
            "gemini": {"model": gemini_model},
            "together": {"model": together_model},
            "deepseek": {"model": deepseek_model},
        }
        save_settings(new_settings)

        with st.spinner(f"Testing {selected_provider}..."):
            success, msg = test_connection()
            if success:
                st.success(msg)
            else:
                st.error(msg)

# ─── Info ───
st.markdown("---")
st.markdown("### ℹ️ Provider Notes")
st.markdown("""
| Provider | Best For | Notes |
|----------|----------|-------|
| **Gemini** | High-quality extraction, fast | Free tier at aistudio.google.com |
| **Together AI** | Open-source models, Qwen 3 | Good balance of quality and cost |
| **DeepSeek** | Cost-effective, strong reasoning | OpenAI-compatible API |
""")

st.caption("🔒 For Streamlit Cloud deployment, add API keys as secrets (GEMINI_API_KEY, TOGETHER_API_KEY, DEEPSEEK_API_KEY) in your app settings.")
