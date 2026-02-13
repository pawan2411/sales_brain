import bcrypt
import json
import os
import streamlit as st

USERS_FILE = os.path.join(os.path.dirname(__file__), "data", "users.json")

# Hardcoded admin credentials (bcrypt hash of 'admin')
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "$2b$12$mm4R9thjiT0.lJ8njlAdmecUJvk7vPacdWwzWdefT93DF1jWWXQ9W"


def _load_users() -> dict:
    """Load users from JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users(users: dict):
    """Save users to JSON file."""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_user(username: str, password: str) -> bool:
    """Create a new user. Returns True if successful, False if user already exists."""
    users = _load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    _save_users(users)
    return True


def authenticate(username: str, password: str) -> bool:
    """Authenticate a user. Checks admin first, then regular users."""
    # Check hardcoded admin
    if username == ADMIN_USERNAME:
        return verify_password(password, ADMIN_PASSWORD_HASH)
    # Check regular users
    users = _load_users()
    if username not in users:
        return False
    return verify_password(password, users[username])


def is_admin() -> bool:
    """Check if the current logged-in user is admin."""
    return st.session_state.get("username") == ADMIN_USERNAME


def login_form():
    """Display login/signup form and manage session state.
    Returns True if user is authenticated."""
    if st.session_state.get("authenticated"):
        return True

    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3rem;
                font-weight: 800;
                margin-bottom: 0.2rem;
            ">Sales Brain</h1>
            <p style="color: #8892b0; font-size: 1.1rem;">RevCortex Buying Process Mastery</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if not username or not password:
                    st.error("Please fill in all fields.")
                elif authenticate(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab_signup:
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_user")
            new_password = st.text_input("Password", type="password", key="signup_pass")
            confirm_password = st.text_input(
                "Confirm Password", type="password", key="signup_confirm"
            )
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if not new_username or not new_password:
                    st.error("Please fill in all fields.")
                elif new_username.lower() == ADMIN_USERNAME:
                    st.error("This username is reserved.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 4:
                    st.error("Password must be at least 4 characters.")
                elif create_user(new_username, new_password):
                    st.success("Account created! Please log in.")
                else:
                    st.error("Username already exists.")

    return False
