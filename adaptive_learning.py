# streamlit_app.py
import streamlit as st
import openai
import csv
import os
from datetime import datetime

# === Configuration ===
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Set this in Streamlit Cloud secrets

# === Functions ===
def generate_lesson():
    prompt = (
        "You are an expert teacher helping a student understand recursion.\n"
        "Give a short, clear explanation (<300 words), including:\n"
        "- A real-world analogy\n- A simple Python example\n- A common mistake to avoid\n"
        "End with a one-line summary tip."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def save_results(name, pre_score, post_score, timestamp):
    filename = "results.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Pre_Score", "Post_Score", "Timestamp"])
        writer.writerow([name, pre_score, post_score, timestamp])

def ask_quiz():
    questions = [
        ("What is the base case in a recursive function?", ["A. Infinite loop", "B. Stopping condition", "C. Loop variable", "D. Recursion depth"], "B. Stopping condition"),
        ("What does this return? def recur(x): if x==0: return 0 else: return x + recur(x-1); recur(3)", ["A. 3", "B. 6", "C. 0", "D. Error"], "B. 6"),
        ("Why can recursion lead to stack overflow?", ["A. Too many variables", "B. Too many loops", "C. Too many function calls", "D. Wrong return type"], "C. Too many function calls")
    ]
    score = 0
    for q, opts, correct in questions:
        user_ans = st.radio(q, opts, key=q)
        if user_ans == correct:
            score += 1
    return score

# === Streamlit UI ===
st.title("📚 LLM-Powered Microlearning Study")
st.subheader("Topic: Recursion in Programming")

name = st.text_input("Enter your name or ID:")

if name:
    st.markdown("### Step 1: Pre-Quiz")
    pre_score = ask_quiz()

    st.markdown("---")
    st.markdown("### Step 2: AI-Generated Microlesson")
    if st.button("Generate Lesson"):
        with st.spinner("Generating your personalized lesson..."):
            lesson = generate_lesson()
            st.success("Done!")
            st.text_area("Your Lesson", lesson, height=300)

    st.markdown("---")
    st.markdown("### Step 3: Post-Quiz")
    post_score = ask_quiz()

    if st.button("Submit My Results"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_results(name, pre_score, post_score, timestamp)
        st.success("✅ Your results have been recorded. Thank you!")
