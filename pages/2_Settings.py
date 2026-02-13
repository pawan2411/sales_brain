import streamlit as st
from llm_providers import load_settings, save_settings, test_connection, get_api_key
from auth import is_admin
from extraction_prompt import DEFAULT_SYSTEM_PROMPT

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
    st.caption("🔑 Admin")
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

st.info("🔒 **API keys are stored locally** in `data/settings.json` (gitignored — never pushed to GitHub). All users share the same keys set by admin.", icon="🔐")

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
    if selected_provider == "gemini":
        st.success("✅ Active provider")

    gemini_key = st.text_input(
        "Gemini API Key",
        value=settings.get("gemini", {}).get("api_key", ""),
        type="password",
        key="gemini_key_input",
        help="Get your key from https://aistudio.google.com/apikey",
    )
    gemini_model = st.text_input(
        "Gemini Model",
        value=settings.get("gemini", {}).get("model", "gemini-2.5-flash"),
        key="gemini_model",
        help="e.g. gemini-2.5-flash, gemini-2.5-pro",
    )

with col2:
    st.markdown("#### 🟣 Together AI")
    if selected_provider == "together":
        st.success("✅ Active provider")

    together_key = st.text_input(
        "Together API Key",
        value=settings.get("together", {}).get("api_key", ""),
        type="password",
        key="together_key_input",
        help="Get your key from https://api.together.xyz/settings/api-keys",
    )
    together_model = st.text_input(
        "Together Model",
        value=settings.get("together", {}).get("model", "Qwen/Qwen3-Next-80B-A3B-Instruct"),
        key="together_model",
        help="e.g. Qwen/Qwen3-Next-80B-A3B-Instruct",
    )

with col3:
    st.markdown("#### 🔵 DeepSeek")
    if selected_provider == "deepseek":
        st.success("✅ Active provider")

    deepseek_key = st.text_input(
        "DeepSeek API Key",
        value=settings.get("deepseek", {}).get("api_key", ""),
        type="password",
        key="deepseek_key_input",
        help="Get your key from https://platform.deepseek.com/api_keys",
    )
    deepseek_model = st.text_input(
        "DeepSeek Model",
        value=settings.get("deepseek", {}).get("model", "deepseek-chat"),
        key="deepseek_model",
        help="e.g. deepseek-chat, deepseek-reasoner",
    )

# ─── System Prompt ───
st.markdown("---")
st.markdown("### 📝 System Prompt")
st.caption("This prompt instructs the AI how to extract and structure deal information. Edit carefully — it controls the quality of deal extraction.")

current_prompt = settings.get("system_prompt", "").strip() or DEFAULT_SYSTEM_PROMPT

prompt_col, reset_col = st.columns([4, 1])
with reset_col:
    st.markdown("<br>", unsafe_allow_html=True)
    reset_prompt = st.button("🔄 Reset to Default", use_container_width=True)

if reset_prompt:
    current_prompt = DEFAULT_SYSTEM_PROMPT
    st.toast("Prompt reset to default. Click Save to apply.")

edited_prompt = st.text_area(
    "System Prompt",
    value=current_prompt,
    height=400,
    label_visibility="collapsed",
    key="system_prompt_editor",
)

st.markdown("---")

# ─── Save & Test ───
save_col, test_col = st.columns(2)

with save_col:
    if st.button("💾 Save Settings", use_container_width=True, type="primary"):
        new_settings = {
            "provider": selected_provider,
            "gemini": {"model": gemini_model, "api_key": gemini_key},
            "together": {"model": together_model, "api_key": together_key},
            "deepseek": {"model": deepseek_model, "api_key": deepseek_key},
            "system_prompt": edited_prompt.strip(),
        }
        # Clear system_prompt key if it matches default (no need to store)
        if new_settings["system_prompt"] == DEFAULT_SYSTEM_PROMPT.strip():
            new_settings["system_prompt"] = ""
        save_settings(new_settings)
        st.success("✅ Settings saved!")
        st.rerun()

with test_col:
    if st.button("🔗 Test Connection", use_container_width=True):
        # Save first so test uses latest keys
        new_settings = {
            "provider": selected_provider,
            "gemini": {"model": gemini_model, "api_key": gemini_key},
            "together": {"model": together_model, "api_key": together_key},
            "deepseek": {"model": deepseek_model, "api_key": deepseek_key},
            "system_prompt": edited_prompt.strip(),
        }
        if new_settings["system_prompt"] == DEFAULT_SYSTEM_PROMPT.strip():
            new_settings["system_prompt"] = ""
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

st.caption("🔒 API keys are stored in `data/settings.json` (gitignored). For Streamlit Cloud, add them as secrets (GEMINI_API_KEY, TOGETHER_API_KEY, DEEPSEEK_API_KEY).")

