# streamlit_app.py
import streamlit as st
import openai
import csv
import os
from datetime import datetime

# === Configuration ===
# Best practice: Initialize the OpenAI client with the API key from Streamlit secrets
# This is the new syntax for the OpenAI v1.x library
try:
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error(f"Could not initialize OpenAI client. Make sure your OPENAI_API_KEY is set in Streamlit secrets. Error: {e}")
    st.stop()


# === Functions ===
def generate_lesson():
    """Generates a lesson using the OpenAI API with the new syntax."""
    prompt = (
        "You are an expert teacher helping a student understand recursion.\n"
        "Give a short, clear explanation (<300 words), including:\n"
        "- A real-world analogy (like Russian nesting dolls).\n"
        "- A simple Python code example (like a factorial function).\n"
        "- A common mistake to avoid (like forgetting the base case).\n"
        "End with a one-line summary tip."
    )
    try:
        # The updated method call: client.chat.completions.create()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        # The response object structure is also updated
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Failed to generate lesson: {e}")
        return None

def save_results(name, pre_score, post_score, timestamp):
    """Saves the study results to a CSV file."""
    # Note: On Streamlit Cloud, the filesystem is ephemeral.
    # This means the CSV file will be reset on every app restart or dyno change.
    # For persistent storage, consider using st.connection() with a database.
    filename = "results.csv"
    file_exists = os.path.isfile(filename)
    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Name", "Pre_Score", "Post_Score", "Timestamp"])
            writer.writerow([name, pre_score, post_score, timestamp])
        return True
    except Exception as e:
        st.error(f"Failed to save results to CSV: {e}")
        return False

def ask_quiz(prefix):
    """Displays a quiz and returns the score. The prefix prevents widget ID conflicts."""
    questions = [
        ("What is the 'base case' in a recursive function?", ["A. An infinite loop condition", "B. The condition that stops the recursion", "C. The variable that is changed in each call", "D. The maximum depth of the recursion"], "B. The condition that stops the recursion"),
        ("What does this Python code return? `def recur(x): if x==0: return 0 else: return x + recur(x-1); recur(3)`", ["A. 3", "B. 6", "C. 0", "D. An error"], "B. 6"),
        ("Why can deep recursion lead to a 'stack overflow' error?", ["A. Because it uses too many variables", "B. Because it creates too many loops", "C. Because it consumes too much memory with nested function calls", "D. Because the return type is wrong"], "C. Because it consumes too much memory with nested function calls")
    ]
    score = 0
    for i, (q, opts, correct) in enumerate(questions):
        # Using a unique key for each radio button is crucial in Streamlit
        user_ans = st.radio(q, opts, key=f"{prefix}_q{i}")
        if user_ans == correct:
            score += 1
    return score

# === Streamlit UI ===

st.title("📚 LLM-Powered Microlearning Study")
st.subheader("Topic: Recursion in Programming")

# Initialize session state to manage the flow of the study
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


# Step 1: Get user's name
if st.session_state.step == "name_input":
    name = st.text_input("Enter your name or a unique ID to begin:")
    if st.button("Start Pre-Quiz"):
        if name:
            st.session_state.name = name
            st.session_state.step = "pre_quiz"
            st.rerun()
        else:
            st.warning("Please enter your name or ID.")

# Step 2: Pre-Quiz
if st.session_state.step == "pre_quiz":
    st.info(f"Welcome, {st.session_state.name}!")
    st.markdown("### Step 1: Pre-Quiz")
    st.markdown("Please answer these questions to the best of your ability.")
    pre_score = ask_quiz(prefix="pre")
    if st.button("Submit Pre-Quiz"):
        st.session_state.pre_score = pre_score
        st.session_state.step = "lesson"
        st.rerun()

# Step 3: AI-Generated Lesson
if st.session_state.step == "lesson":
    st.markdown("---")
    st.markdown("### Step 2: AI-Generated Microlesson")
    st.write("Click the button below to generate your personalized lesson on recursion.")
    
    if st.button("Generate My Lesson"):
        with st.spinner("👩‍🏫 Generating your lesson... this may take a moment."):
            lesson_content = generate_lesson()
            if lesson_content:
                st.session_state.lesson = lesson_content
                st.success("Lesson generated!")
    
    if st.session_state.lesson:
        st.text_area("Your Lesson on Recursion", st.session_state.lesson, height=350)
        if st.button("Continue to Post-Quiz"):
            st.session_state.step = "post_quiz"
            st.rerun()

# Step 4: Post-Quiz
if st.session_state.step == "post_quiz":
    st.markdown("---")
    st.markdown("### Step 3: Post-Quiz")
    st.markdown("Now that you've completed the lesson, please take the quiz again.")
    post_score = ask_quiz(prefix="post")
    if st.button("Submit Post-Quiz"):
        st.session_state.post_score = post_score
        st.session_state.step = "results"
        st.rerun()

# Step 5: Show and Save Results
if st.session_state.step == "results":
    st.markdown("---")
    st.balloons()
    st.header("🎉 Study Complete! 🎉")
    st.write(f"**Name:** {st.session_state.name}")
    st.write(f"**Pre-Quiz Score:** {st.session_state.pre_score} / 3")
    st.write(f"**Post-Quiz Score:** {st.session_state.post_score} / 3")

    if st.button("Save My Results"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if save_results(st.session_state.name, st.session_state.pre_score, st.session_state.post_score, timestamp):
            st.success("✅ Your results have been recorded. Thank you for participating!")
            st.session_state.step = "finished" # Move to a final state
        else:
            st.error("There was an issue saving your results. Please try again.")

if st.session_state.step == "finished":
    st.info("You can now close this window.")
