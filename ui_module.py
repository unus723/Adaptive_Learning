# ui_module.py
import streamlit as st
from datetime import datetime
from lesson_module import LessonGenerator
from quiz_module import Quiz
from database_module import save_results_db, get_db_connection
import pandas as pd

lesson_gen = LessonGenerator()
quiz = Quiz()

def render_ui(username, topic):
    st.title("📚 Microlearning Study")
    st.subheader(f"Topic: {topic}")

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
        name = st.text_input("Enter your name to begin:")
        if st.button("Start Pre-Quiz"):
            if name:
                st.session_state.name = name
                st.session_state.step = "pre_quiz"
                st.rerun()
            else:
                st.warning("Please enter your name.")

    if st.session_state.step == "pre_quiz":
        st.info(f"Welcome, {st.session_state.name}!")
        st.markdown("### Step 1: Pre-Quiz")
        st.markdown("Please answer these questions to the best of your ability.")
        pre_score = quiz.ask_quiz(prefix="pre", topic=topic)
        if st.button("Submit Pre-Quiz"):
            st.session_state.pre_score = pre_score
            st.session_state.step = "lesson"
            st.rerun()

    if st.session_state.step == "lesson":
        st.markdown("---")
        st.markdown("### Step 2: Microlesson")
        st.write("Click the button below to generate your personalized lesson.")
        if st.button("Generate My Lesson"):
            with st.spinner("Generating your lesson..."):
                lesson_content = lesson_gen.generate_lesson(topic)
                if lesson_content:
                    st.session_state.lesson = lesson_content
                    st.success("Lesson generated!")

        if st.session_state.lesson:
            st.text_area("Your Lesson", st.session_state.lesson, height=350)
            if st.button("Continue to Post-Quiz"):
                st.session_state.step = "post_quiz"
                st.rerun()

    if st.session_state.step == "post_quiz":
        st.markdown("---")
        st.markdown("### Step 3: Post-Quiz")
        post_score = quiz.ask_quiz(prefix="post", topic=topic)
        if st.button("Submit Post-Quiz"):
            st.session_state.post_score = post_score
            st.session_state.step = "results"
            st.rerun()

    if st.session_state.step == "results":
        st.balloons()
        st.header("🎉 Study Complete! 🎉")
        st.write(f"**Name:** {st.session_state.name}")
        st.write(f"**Pre-Quiz Score:** {st.session_state.pre_score} / 3")
        st.write(f"**Post-Quiz Score:** {st.session_state.post_score} / 3")

        if st.button("Save My Results"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_results_db(
                name=st.session_state.name,
                pre_score=st.session_state.pre_score,
                post_score=st.session_state.post_score,
                username=username,
                timestamp=timestamp
            )
            st.success("✅ Results saved successfully.")
            st.session_state.step = "finished"

    if st.session_state.step == "finished":
        st.info("You can now close the window or restart to try a new topic.")

