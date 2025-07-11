# main.py
import streamlit as st
from auth_module import Authenticator
from ui_module import render_ui

# Initialize authentication object
auth = Authenticator()

# Set up login session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Handle Authentication (Login/Register)
if not st.session_state.logged_in:
    st.subheader("\U0001F512 Micro Learning")
    auth_mode = st.radio("LOGIN/SIGNUP", ["Login if you have an account", "First time users: Register"], horizontal=True, key="auth_mode_radio")

    if auth_mode == "Login":
        login_successful = auth.login_form()
        if login_successful:
            st.rerun()
        st.stop()
    elif auth_mode == "Register":
        auth.registration_form()
        st.stop()

# User is authenticated: render app UI
render_ui(st.session_state.username)

# Show logout button at bottom
if st.session_state.logged_in:
    if st.button("Logout", key="logout_button"):
        st.session_state.clear()
        st.success("You have been logged out.")
        st.rerun()
