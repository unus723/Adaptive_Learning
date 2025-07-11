import streamlit as st
from database_module import register_user, verify_user

class Authenticator:
    def __init__(self):
        self.username = ""

    def login_form(self):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", key="login_button"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
                return True
            else:
                st.error("Invalid username or password.")
        return False

    def registration_form(self):
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        if st.button("Register", key="register_button"):
            if register_user(username, password):
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username already exists. Please choose another.")

    def logout(self):
        if st.session_state.get("logged_in"):
            if st.button("Logout", key="logout_button"):
                st.session_state.clear()
                st.success("You have been logged out.")
