# main.py
import streamlit as st
from auth_module import Authenticator
from ui_module import render_ui
from lesson_module import LessonGenerator
from quiz_module import Quiz

# Initialize modules
auth = Authenticator()
lesson_gen = LessonGenerator()
quiz = Quiz()

# Set up login session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Handle Authentication (Login/Register)
if not st.session_state.logged_in:
    st.subheader("\U0001F512 Micro Learning")
    st.subheader("Access Your Personalized Learning Journey")
    auth_mode = st.radio("Login or Register:", ["Login", "Register"], horizontal=True, key="auth_mode_radio")

    if auth_mode == "Login":
        login_successful = auth.login_form()
        if login_successful:
            st.rerun()
        st.stop()
    elif auth_mode == "Register":
        auth.registration_form()
        st.stop()

# Topic selection
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = None
st.sidebar.subheader("Study Options")
topics = [
    "Supervised Learning",
    "Unsupervised Learning",
    "Reinforcement Learning",
    "Neural Networks",
    "Deep Learning",
    "Natural Language Processing",
    "Computer Vision",
    "Model Evaluation",
    "Feature Engineering",
    "Ensemble Methods",
    "Clustering",
    "Dimensionality Reduction",
    "Time Series Analysis"
]
if 'topic_select_radio' not in st.session_state:
    st.session_state.topic_select_radio = topics[0]  # Default to first topic
st.sidebar.radio("Choose a topic:", topics, key="topic_select_radio")
st.session_state.selected_topic = st.session_state.topic_select_radio

# User is authenticated: render app UI with selected topic
render_ui(st.session_state.username, st.session_state.selected_topic)

# Show logout button at bottom
if st.session_state.logged_in:
    col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
    with col2:
        if st.button("Logout", key="logout_button"):
            st.session_state.clear()
            st.success("You have been logged out.")
            st.rerun()

