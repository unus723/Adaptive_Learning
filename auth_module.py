from datetime import datetime
import streamlit as st
from database import save_user_db

class Authenticator:
    def __init__(self):
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'username' not in st.session_state:
            st.session_state.username = ""

    def login(self):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username and password == st.secrets.get("DASHBOARD_PASSWORD"):
                st.session_state.authenticated = True
                st.session_state.username = username
                save_user_db(username)
                st.rerun()
            else:
                st.error("Invalid credentials.")

    def logout(self):
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()

    def is_authenticated(self):
        return st.session_state.get("authenticated", False)
