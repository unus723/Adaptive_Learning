import streamlit as st
from datetime import datetime
from auth_module import Authenticator
from lesson_module import LessonGenerator
from quiz_module import Quiz
from database_module import save_results_db, get_db_connection # Ensure get_db_connection is imported
import pandas as pd

# Initialize Modules
auth = Authenticator()
lesson_gen = LessonGenerator()
quiz = Quiz()

# === User Authentication ===
# Ensure login state is initialized
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state: # Also initialize username for consistency
    st.session_state.username = None

# Authentication flow: show login/register if not logged in, then stop
if not st.session_state.logged_in:
    st.subheader("🔐 Authentication")

    auth_mode = st.radio("Choose an option", ["Login", "Register"], horizontal=True, key="auth_mode_radio") # Added key

    if auth_mode == "Login":
        login_successful = auth.login_form()
        if login_successful:
            st.rerun() # Rerun immediately on successful login
        # If login was NOT successful, or user hasn't tried yet, stop.
        # This prevents the rest of the app from rendering until authenticated.
        st.stop() # This stop will always be hit if not logged_in and login_successful is False

    elif auth_mode == "Register":
        auth.registration_form()
        st.stop() # Stop after showing registration form
    
    # This st.stop() should ideally catch any case where the user is not logged in
    # and the authentication forms are being displayed.
    st.stop() # Redundant but safe if previous stops are missed for some reason

# --- If execution reaches here, the user IS logged in ---
# All content below this point is for authenticated users

st.write(f"Welcome, {st.session_state.username}!") # This line will now only show for logged-in users

# === App Title ===
st.title("\U0001F4DA Microlearning Study")
st.subheader("Topic: Recursion")

# === Session State Initialization for Study Workflow ===
# Only initialize these if they don't exist, and only for logged-in users
if 'step' not in st.session_state:
    st.session_state.step = "name_input"
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'pre_score' not in st.session_state:
    st.session_state.pre_score = 0
if 'post_score' not in st.session_state:
    st.session_state.post_score = 0
if 'lesson' not in st.session_state:
    st.session_state.lesson = "" 

# === Study Workflow ===
if st.session_state.step == "name_input":
    name = st.text_input("Enter your name or a unique ID to begin:", key="name_input_text") # Added key
    if st.button("Start Pre-Quiz", key="start_pre_quiz_button"): # Added key
        if name:
            st.session_state.name = name
            st.session_state.step = "pre_quiz"
            st.rerun()
        else:
            st.warning("Please enter your name or ID.")

if st.session_state.step == "pre_quiz":
    st.info(f"Welcome, {st.session_state.name}!")
    st.markdown("### Step 1: Pre-Quiz")
    st.markdown("Please answer these questions to the best of your ability.")
    pre_score = quiz.ask_quiz(prefix="pre") # Assuming quiz.ask_quiz handles its own keys
    if st.button("Submit Pre-Quiz", key="submit_pre_quiz_button"): # Added key
        st.session_state.pre_score = pre_score
        st.session_state.step = "lesson"
        st.rerun()

if st.session_state.step == "lesson":
    st.markdown("---")
    st.markdown("### Step 2: Microlesson")
    st.write("Click the button below to generate your personalized lesson on recursion.")
    if st.button("Generate My Lesson", key="generate_lesson_button"): # Added key
        with st.spinner("\U0001F469‍\U0001F3EB Generating your lesson... this may take a moment."):
            lesson_content = lesson_gen.generate_lesson()
            if lesson_content:
                st.session_state.lesson = lesson_content
                st.success("Lesson generated!")

    if st.session_state.lesson:
        st.text_area("Your Lesson on Recursion", st.session_state.lesson, height=350, key="lesson_text_area") # Added key
        if st.button("Continue to Post-Quiz", key="continue_post_quiz_button"): # Added key
            st.session_state.step = "post_quiz"
            st.rerun()

if st.session_state.step == "post_quiz":
    st.markdown("---")
    st.markdown("### Step 3: Post-Quiz")
    st.markdown("Now that you've completed the lesson, please take the quiz again.")
    post_score = quiz.ask_quiz(prefix="post") # Assuming quiz.ask_quiz handles its own keys
    if st.button("Submit Post-Quiz", key="submit_post_quiz_button"): # Added key
        st.session_state.post_score = post_score
        st.session_state.step = "results"
        st.rerun()

if st.session_state.step == "results":
    st.markdown("---")
    st.balloons()
    st.header("\U0001F389 Study Complete! \U0001F389")
    st.write(f"**Name:** {st.session_state.name}")
    st.write(f"**Pre-Quiz Score:** {st.session_state.pre_score} / 3")
    st.write(f"**Post-Quiz Score:** {st.session_state.post_score} / 3")
    # This button should also have a key if it's not already handled by save_results_db
    if st.button("Save My Results", key="save_results_button"): # Added key
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_results_db(st.session_state.name, st.session_state.pre_score, st.session_state.post_score, st.session_state.username, timestamp)
        st.session_state.step = "finished"

if st.session_state.step == "finished":
    st.info("You can now close this window or return to login.")

# === Dashboard (restricted) ===
# This dashboard should ideally only be shown to logged-in users.
# The `st.stop()` above handles this, but if you want to be explicit:
if st.session_state.logged_in:  # Explicit check
    with st.expander("Results"):
        st.header("Results")
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Ensure the 'results' table is created if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    pre_score INTEGER,
                    post_score INTEGER,
                    timestamp TIMESTAMP
                )
            """)
            conn.commit()  # Commit the table creation if it happened

            cur.execute("SELECT name, pre_score, post_score, timestamp FROM results WHERE username = %s ORDER BY timestamp DESC;", (st.session_state.username,))
            results = cur.fetchall()
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df)
            else:
                st.info("No study results found yet.")
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Error loading results from database: {e}")

# === Logout Button (single instance, at the very end for logged-in users) ===
# This ensures it's only rendered once if the user is logged in.
if st.session_state.logged_in:
    # Using columns for placement, e.g., to the right
    col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
    with col2:  # Place it in the center column
        if st.button("Logout", key="main_app_logout_button"):
            st.session_state.clear()
            st.success("You have been logged out.")
            st.rerun()