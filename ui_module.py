# ui_module.py
import streamlit as st
from datetime import datetime
from lesson_module import LessonGenerator
from quiz_module import Quiz
from database_module import save_results_db, get_db_connection
import pandas as pd

lesson_gen = LessonGenerator()
quiz = Quiz()

def render_ui(username):
    st.title("\U0001F4DA Microlearning Study")
    st.subheader("Topic: Recursion")

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

    if st.session_state.step == "name_input":
        name = st.text_input("Enter your name or a unique ID to begin:", key="name_input_text")
        if st.button("Start Pre-Quiz", key="start_pre_quiz_button"):
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
        pre_score = quiz.ask_quiz(prefix="pre")
        if st.button("Submit Pre-Quiz", key="submit_pre_quiz_button"):
            st.session_state.pre_score = pre_score
            st.session_state.step = "lesson"
            st.rerun()

    if st.session_state.step == "lesson":
        st.markdown("---")
        st.markdown("### Step 2: Microlesson")
        st.write("Click the button below to generate your personalized lesson on recursion.")
        if st.button("Generate My Lesson", key="generate_lesson_button"):
            with st.spinner("\U0001F469‍\U0001F3EB Generating your lesson... this may take a moment."):
                lesson_content = lesson_gen.generate_lesson()
                if lesson_content:
                    st.session_state.lesson = lesson_content
                    st.success("Lesson generated!")

        if st.session_state.lesson:
            st.text_area("Your Lesson on Recursion", st.session_state.lesson, height=350, key="lesson_text_area")
            if st.button("Continue to Post-Quiz", key="continue_post_quiz_button"):
                st.session_state.step = "post_quiz"
                st.rerun()

    if st.session_state.step == "post_quiz":
        st.markdown("---")
        st.markdown("### Step 3: Post-Quiz")
        st.markdown("Now that you've completed the lesson, please take the quiz again.")
        post_score = quiz.ask_quiz(prefix="post")
        if st.button("Submit Post-Quiz", key="submit_post_quiz_button"):
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
        if st.button("Save My Results", key="save_results_button"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_results_db(
                st.session_state.name,
                st.session_state.pre_score,
                st.session_state.post_score,
                username,
                timestamp
            )
            st.session_state.step = "finished"

    if st.session_state.step == "finished":
        st.info("You can now close this window or return to login.")

    if st.session_state.logged_in:
        with st.expander("Results"):
            st.header("Results")
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT name, pre_score, post_score, timestamp FROM results WHERE username = %s ORDER BY timestamp DESC;", (username,))
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
