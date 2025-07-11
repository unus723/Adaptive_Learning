# quiz_module.py
import streamlit as st
import openai
import ast

class Quiz:
    def __init__(self):
        try:
            self.client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        except Exception as e:
            st.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def generate_quiz(self, topic):
        if not self.client:
            return []

        prompt = (
            f"Generate 3 multiple-choice questions on the topic '{topic}'. "
            f"Each question should have exactly 4 options and specify the correct answer. "
            f"Format as a Python list of dictionaries like this: \n"
            f"[{{'question': '...', 'options': ['A. ...', 'B. ...', 'C. ...', 'D. ...'], 'answer': 'A. ...'}}, ...]"
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            result = response.choices[0].message.content.strip()
            questions = ast.literal_eval(result)  # Use safer parser
            return questions
        except Exception as e:
            st.error(f"Failed to generate quiz: {e}")
            return []

    def ask_dynamic_quiz(self, prefix, questions):
        score = 0
        with st.expander(f"{prefix.capitalize()} Quiz", expanded=True):
            for i, q in enumerate(questions):
                user_ans = st.radio(q['question'], q['options'], key=f"{prefix}_q{i}")
                if user_ans == q['answer']:
                    score += 1
        return score

    def ask_quiz(self, prefix, topic):
        if f'{prefix}_questions' not in st.session_state:
            st.session_state[f'{prefix}_questions'] = self.generate_quiz(topic)

        questions = st.session_state[f'{prefix}_questions']

        if not questions:
            st.error("Failed to generate quiz questions.")
            return 0

        score = self.ask_dynamic_quiz(prefix, questions)
        return score
