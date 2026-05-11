import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from frontend.utils.api_client import login, register, get_me

st.set_page_config(page_title="AI Robo-Advisor", page_icon="📈", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.token is None:
    st.title("AI Robo-Advisor Platform")
    st.markdown("Personalized investment advice powered by machine learning and AI.")
    st.divider()

    tab_login, tab_register = st.tabs(["Login", "Create Account"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            result = login(email, password)
            if "access_token" in result:
                user_data = get_me(result["access_token"])
                if "name" in user_data:
                    st.session_state.token = result["access_token"]
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error(f"Login succeeded but could not load profile: {user_data}")
            else:
                st.error(result.get("detail", "Login failed"))

    with tab_register:
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email_r = st.text_input("Email")
            password_r = st.text_input("Password", type="password")
            submitted_r = st.form_submit_button("Create Account", use_container_width=True)
        if submitted_r:
            result = register(name, email_r, password_r)
            if "access_token" in result:
                user_data = get_me(result["access_token"])
                if "name" in user_data:
                    st.session_state.token = result["access_token"]
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error(f"Account created but could not load profile: {user_data}")
            else:
                st.error(result.get("detail", "Registration failed"))

else:
    user = st.session_state.user
    if not user or "name" not in user:
        st.error(f"Session error: {user}")
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()
    st.sidebar.success(f"Logged in as **{user['name']}**")
    if user.get("risk_score"):
        from backend.models.risk import risk_label
        st.sidebar.info(f"Risk profile: **{risk_label(user['risk_score'])}** ({user['risk_score']}/10)")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

    st.title("Welcome back, " + user["name"])
    st.info("Use the sidebar to navigate to Dashboard, Portfolio, AI Advisor, or Market.")
