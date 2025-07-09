import streamlit as st

class Quiz:
    def __init__(self):
        self.questions = [
            (
                "What is the 'base case' in a recursive function?",
                [
                    "A. An infinite loop condition",
                    "B. The condition that stops the recursion",
                    "C. The variable that is changed in each call",
                    "D. The maximum depth of the recursion"
                ],
                "B. The condition that stops the recursion"
            ),
            (
                "What does this Python code return? `def recur(x): if x==0: return 0 else: return x + recur(x-1); recur(3)`",
                ["A. 3", "B. 6", "C. 0", "D. An error"],
                "B. 6"
            ),
            (
                "Why can deep recursion lead to a 'stack overflow' error?",
                [
                    "A. Because it uses too many variables",
                    "B. Because it creates too many loops",
                    "C. Because it consumes too much memory with nested function calls",
                    "D. Because the return type is wrong"
                ],
                "C. Because it consumes too much memory with nested function calls"
            )
        ]

    def ask_quiz(self, prefix):
        score = 0
        for i, (q, opts, correct) in enumerate(self.questions):
            user_ans = st.radio(q, opts, key=f"{prefix}_q{i}")
            if user_ans == correct:
                score += 1
        return score