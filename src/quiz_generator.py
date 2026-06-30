"""
BioBridge AI - Quiz Generator (V1)
-----------------------------------
Generates 5 MCQs for biotechnology concepts using Gemini API.
Strict JSON output for Streamlit quiz interface.
"""

import os
import json
import re
import time
import google.generativeai as genai
from dotenv import load_dotenv

from src.logger import log_event
from src.constants import (
    FEATURE_QUIZ_GENERATOR,
    STATUS_SUCCESS,
    STATUS_ERROR,
)

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_quiz(topic):
    start_time = time.time()

    # ---------------------------
    # Input validation
    # ---------------------------
    if not topic or not topic.strip():
        latency_ms = int((time.time() - start_time) * 1000)

        log_event(
            feature=FEATURE_QUIZ_GENERATOR,
            status=STATUS_ERROR,
            user_input=topic,
            latency_ms=latency_ms,
            error_message="No topic provided.",
        )

        return {
            "status": "error",
            "message": "Please enter a valid biology or biotechnology topic."
        }

    prompt = f"""
You are BioBridge AI V1 Quiz Generator, an AI tutor for biotechnology students.

TASK:
Generate EXACTLY 5 multiple-choice questions for the given topic.

TOPIC:
{topic}

STRICT RULES:
- Output ONLY valid JSON
- Do NOT include markdown, backticks, or explanations outside JSON
- Generate EXACTLY 5 questions
- Each question must have 4 options (A, B, C, D)
- Correct answer must be exactly one of: "A", "B", "C", "D"
- Questions must be biologically accurate
- Avoid ambiguous or trick questions
- Distribute correct answers randomly across A-D
- Cover different sub-aspects of the topic
- Keep explanations short and educational
- No greetings, no introductions, no extra text

OFF-TOPIC HANDLING:
- If topic is NOT biology or biotechnology, return ONLY:
{{
  "status": "error",
  "message": "BioBridge AI V1 Quiz Generator supports only biology and biotechnology topics."
}}

OUTPUT FORMAT (STRICT JSON):

{{
  "status": "success",
  "questions": [
    {{
      "question": "Question text here",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Short explanation of why this answer is correct."
    }}
  ]
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # ---------------------------
        # Clean markdown if Gemini adds it accidentally
        # ---------------------------
        if text.startswith("```"):
            text = re.sub(r"```(?:json)?", "", text)
            text = text.replace("```", "").strip()

        # ---------------------------
        # Parse JSON safely
        # ---------------------------
        quiz_data = json.loads(text)

        # ---------------------------
        # Basic structural validation
        # ---------------------------
        if "questions" not in quiz_data or len(quiz_data["questions"]) != 5:
            latency_ms = int((time.time() - start_time) * 1000)

            log_event(
                feature=FEATURE_QUIZ_GENERATOR,
                status=STATUS_ERROR,
                user_input=topic,
                latency_ms=latency_ms,
                error_message="Invalid quiz format generated.",
            )

            return {
                "status": "error",
                "message": "Invalid quiz format generated. Please try again."
            }

        latency_ms = int((time.time() - start_time) * 1000)

        log_event(
            feature=FEATURE_QUIZ_GENERATOR,
            status=STATUS_SUCCESS,
            user_input=topic,
            latency_ms=latency_ms,
        )

        return quiz_data

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)

        log_event(
            feature=FEATURE_QUIZ_GENERATOR,
            status=STATUS_ERROR,
            user_input=topic,
            latency_ms=latency_ms,
            error_message=str(e),
        )

        # Never expose raw errors to user (clean UX for Streamlit app)
        return {
            "status": "error",
            "message": "Couldn't generate quiz right now. Please try again."
        }