import openai
import streamlit as st

class LessonGenerator:
    def __init__(self):
        try:
            self.client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        except Exception as e:
            st.error(f"Could not initialize OpenAI client. Error: {e}")
            st.stop()

    def generate_lesson(self):
        prompt = (
            "You are an expert teacher helping a student understand recursion.\n"
            "Give a short, clear explanation (<300 words), including:\n"
            "- A real-world analogy (like Russian nesting dolls).\n"
            "- A simple Python code example (like a factorial function).\n"
            "- A common mistake to avoid (like forgetting the base case).\n"
            "End with a one-line summary tip."
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Failed to generate lesson: {e}")
            return None
