import streamlit as st
from src.mnemonic_generator import generate_mnemonic
from src.concept_explainer import explain_concept
from src.quiz_generator import generate_quiz
from src.doubt_solver import solve_doubt


# -----------------------------
# APP TITLE
# -----------------------------
st.title("🧬 BioBridge AI")


# -----------------------------
# FEATURE SELECTOR
# -----------------------------
feature = st.selectbox(
    "Choose a feature",
    ["Mnemonic Generator", "Concept Explainer", "Quiz Generator", "Doubt Solver"]
)


# =========================================================
# 🟢 MNEMONIC GENERATOR (UNCHANGED)
# =========================================================
if feature == "Mnemonic Generator":

    st.subheader("🧠 Mnemonic Generator")
    st.write("Generate easy biology mnemonics for studying.")

    topic = st.text_input("Enter a biology topic or list:")

    if st.button("Generate Mnemonic"):
        if topic:
            result = generate_mnemonic(topic)
            st.markdown(result)
        else:
            st.warning("Please enter a topic.")


# =========================================================
# 🔵 CONCEPT EXPLAINER (UNCHANGED)
# =========================================================
elif feature == "Concept Explainer":

    st.subheader("📘 Concept Explainer")
    st.write("Get structured biology concept explanations.")

    if "ce_stage" not in st.session_state:
        st.session_state.ce_stage = "input"
        st.session_state.ce_concept = ""
        st.session_state.ce_difficulty = "Beginner"
        st.session_state.ce_result = ""

    def reset_ce():
        st.session_state.ce_stage = "input"
        st.session_state.ce_concept = ""
        st.session_state.ce_result = ""

    if st.session_state.ce_stage == "input":

        concept = st.text_input(
            "Enter a biology concept:",
            value=st.session_state.ce_concept
        )

        difficulty = st.selectbox(
            "Select Difficulty",
            ["Beginner", "Intermediate", "Advanced"]
        )

        if st.button("Continue"):
            if concept:
                st.session_state.ce_concept = concept
                st.session_state.ce_difficulty = difficulty
                st.session_state.ce_stage = "confirm"
                st.rerun()
            else:
                st.warning("Please enter a concept.")

    elif st.session_state.ce_stage == "confirm":

        st.subheader("Confirm Your Input")
        st.write("**Concept:**", st.session_state.ce_concept)
        st.write("**Difficulty:**", st.session_state.ce_difficulty)

        if st.button("✏️ Edit"):
            st.session_state.ce_stage = "input"
            st.rerun()

        if st.button("🚀 Generate Explanation"):
            result = explain_concept(
                st.session_state.ce_concept,
                st.session_state.ce_difficulty
            )
            st.session_state.ce_result = result
            st.session_state.ce_stage = "result"
            st.rerun()

    elif st.session_state.ce_stage == "result":

        st.subheader("📘 Explanation")
        st.markdown(st.session_state.ce_result)

        if st.button("🔄 Try Another"):
            reset_ce()
            st.rerun()


# =========================================================
# 🟣 QUIZ GENERATOR (UNCHANGED)
# =========================================================
elif feature == "Quiz Generator":

    st.subheader("📝 Quiz Generator")
    st.write("Test your biology knowledge with MCQs.")

    if "qz_stage" not in st.session_state:
        st.session_state.qz_stage = "input"
        st.session_state.qz_topic = ""
        st.session_state.qz_data = {}
        st.session_state.qz_answers = {}

    def reset_quiz():
        st.session_state.qz_stage = "input"
        st.session_state.qz_topic = ""
        st.session_state.qz_data = {}
        st.session_state.qz_answers = {}

    # -----------------------------
    # STAGE 1: INPUT
    # -----------------------------
    if st.session_state.qz_stage == "input":

        topic = st.text_input(
            "Enter a biology/biotechnology topic:",
            value=st.session_state.qz_topic
        )

        if st.button("Generate Quiz"):
            if topic:
                st.session_state.qz_topic = topic
                result = generate_quiz(topic)

                if result["status"] == "success":
                    st.session_state.qz_data = result
                    st.session_state.qz_stage = "quiz"
                    st.rerun()
                else:
                    st.error(result["message"])
            else:
                st.warning("Please enter a topic.")

    # -----------------------------
    # STAGE 2: QUIZ
    # -----------------------------
    elif st.session_state.qz_stage == "quiz":

        st.subheader("Answer the Questions")

        questions = st.session_state.qz_data["questions"]

        for i, q in enumerate(questions):
            st.write(f"**Q{i+1}. {q['question']}**")

            options = q["options"]

            answer = st.radio(
                f"Select answer for Q{i+1}",
                ["A", "B", "C", "D"],
                format_func=lambda x, options=options: f"{x}. {options[x]}",
                key=f"q_{i}"
            )

            st.session_state.qz_answers[i] = answer
            st.write("")

        if st.button("Submit Quiz"):

            score = 0
            results = []

            for i, q in enumerate(questions):
                user_ans = st.session_state.qz_answers[i]
                correct_ans = q["correct_answer"]

                if user_ans == correct_ans:
                    score += 1

                results.append({
                    "question": q["question"],
                    "user": user_ans,
                    "correct": correct_ans,
                    "explanation": q["explanation"]
                })

            st.session_state.qz_result = {
                "score": score,
                "total": len(questions),
                "results": results
            }

            st.session_state.qz_stage = "result"
            st.rerun()

    # -----------------------------
    # STAGE 3: RESULT
    # -----------------------------
    elif st.session_state.qz_stage == "result":

        st.subheader("📊 Your Result")

        st.success(
            f"Score: {st.session_state.qz_result['score']} / {st.session_state.qz_result['total']}"
        )

        st.write("---")

        for r in st.session_state.qz_result["results"]:

            st.write(f"**Q:** {r['question']}")
            st.write(f"Your Answer: {r['user']}")
            st.write(f"Correct Answer: {r['correct']}")
            st.write(f"Explanation: {r['explanation']}")
            st.write("---")

        if st.button("🔄 Try Another Quiz"):
            reset_quiz()
            st.rerun()


# =========================================================
# 🟠 DOUBT SOLVER (NEW FEATURE - FINAL INTEGRATION)
# =========================================================
elif feature == "Doubt Solver":

    st.subheader("💡 Doubt Solver")
    st.write("Ask any biology or biotechnology doubt.")

    question = st.text_area("Enter your doubt:")

    if st.button("Solve Doubt"):

        if question and question.strip():

            result = solve_doubt(question)
            st.markdown(result)

        else:
            st.warning("Please enter a question.")
            