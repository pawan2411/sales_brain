"""
Unified LLM provider interface.
API keys are NEVER persisted to disk — they live only in Streamlit session state.
Provider/model preferences are saved to a local config file.
"""

import json
import os
import re
import streamlit as st

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "data", "settings.json")

DEFAULT_SETTINGS = {
    "provider": "gemini",
    "gemini": {
        "model": "gemini-2.5-flash"
    },
    "together": {
        "model": "Qwen/Qwen3-Next-80B-A3B-Instruct"
    },
    "deepseek": {
        "model": "deepseek-chat"
    }
}


def load_settings() -> dict:
    """Load settings from config file (no API keys — those are session-only)."""
    settings = json.loads(json.dumps(DEFAULT_SETTINGS))  # deep copy
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            saved = json.load(f)
            # Merge saved into defaults
            settings["provider"] = saved.get("provider", settings["provider"])
            for provider in ("gemini", "together", "deepseek"):
                if provider in saved:
                    settings[provider]["model"] = saved[provider].get("model", settings[provider]["model"])
    return settings


def save_settings(settings: dict):
    """Save settings to config file. API keys are explicitly excluded."""
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    # Strip any API keys — never persist them
    safe_settings = {
        "provider": settings.get("provider", "gemini"),
        "gemini": {"model": settings.get("gemini", {}).get("model", "gemini-2.5-flash")},
        "together": {"model": settings.get("together", {}).get("model", "Qwen/Qwen3-Next-80B-A3B-Instruct")},
        "deepseek": {"model": settings.get("deepseek", {}).get("model", "deepseek-chat")},
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(safe_settings, f, indent=2)


def get_api_key(provider: str) -> str:
    """Get API key from session state (memory only). Falls back to st.secrets for Streamlit Cloud."""
    # 1. Check session state (set by user in Settings page)
    key = st.session_state.get(f"{provider}_api_key", "")
    if key:
        return key
    # 2. Fallback to st.secrets (for Streamlit Cloud deployment)
    try:
        secrets_key = f"{provider.upper()}_API_KEY"
        return st.secrets.get(secrets_key, "")
    except Exception:
        return ""


def set_api_key(provider: str, api_key: str):
    """Store API key in session state only (never on disk)."""
    st.session_state[f"{provider}_api_key"] = api_key


def _parse_json_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences."""
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON object found in response: {text[:200]}")
    depth = 0
    end = start
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return json.loads(text[start:end])


def _call_gemini(messages: list[dict], settings: dict, api_key: str) -> str:
    """Call Google Gemini API."""
    from google import genai

    client = genai.Client(api_key=api_key)

    system_instruction = None
    contents = []
    for msg in messages:
        if msg["role"] == "system":
            system_instruction = msg["content"]
        else:
            contents.append(msg["content"])

    response = client.models.generate_content(
        model=settings["gemini"]["model"],
        contents=contents,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.1,
        ),
    )
    return response.text


def _call_together(messages: list[dict], settings: dict, api_key: str) -> str:
    """Call Together AI API."""
    from together import Together

    client = Together(api_key=api_key)
    response = client.chat.completions.create(
        model=settings["together"]["model"],
        messages=messages,
        temperature=0.1,
        max_tokens=4096,
    )
    return response.choices[0].message.content


def _call_deepseek(messages: list[dict], settings: dict, api_key: str) -> str:
    """Call DeepSeek API via OpenAI-compatible endpoint."""
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )
    response = client.chat.completions.create(
        model=settings["deepseek"]["model"],
        messages=messages,
        temperature=0.1,
        max_tokens=4096,
    )
    return response.choices[0].message.content


def extract_deal_info(messages: list[dict]) -> dict:
    """Call the selected LLM provider and return parsed JSON."""
    settings = load_settings()
    provider = settings.get("provider", "gemini")
    api_key = get_api_key(provider)

    if not api_key:
        raise ValueError(
            f"No API key set for {provider}. "
            f"Please enter it in the Settings page (keys are session-only, never saved to disk)."
        )

    call_fn = {
        "gemini": _call_gemini,
        "together": _call_together,
        "deepseek": _call_deepseek,
    }

    if provider not in call_fn:
        raise ValueError(f"Unknown provider: {provider}")

    raw_response = call_fn[provider](messages, settings, api_key)
    return _parse_json_response(raw_response)


def test_connection() -> tuple[bool, str]:
    """Test the current LLM provider connection."""
    settings = load_settings()
    provider = settings.get("provider", "gemini")
    api_key = get_api_key(provider)

    if not api_key:
        return False, f"No API key set for {provider}. Enter it above (session-only)."

    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Reply with exactly: CONNECTION_OK"},
        ]
        call_fn = {
            "gemini": _call_gemini,
            "together": _call_together,
            "deepseek": _call_deepseek,
        }
        model = settings.get(provider, {}).get("model", "N/A")
        response = call_fn[provider](messages, settings, api_key)
        if "CONNECTION_OK" in response:
            return True, f"✅ Connected to {provider} ({model})"
        else:
            return True, f"✅ Connected to {provider} (response: {response[:50]})"
    except Exception as e:
        return False, f"❌ Connection failed: {str(e)}"
