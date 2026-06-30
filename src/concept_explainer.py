"""
BioBridge AI - Concept Explainer (V1)
--------------------------------------
Explains biology/biotechnology concepts in a structured format using Gemini API.
"""

import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

from src.logger import log_event
from src.constants import (
    FEATURE_CONCEPT_EXPLAINER,
    STATUS_SUCCESS,
    STATUS_ERROR,
)

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")


def explain_concept(concept, difficulty):
    start_time = time.time()

    if not concept or not concept.strip():
        latency_ms = int((time.time() - start_time) * 1000)

        log_event(
            feature=FEATURE_CONCEPT_EXPLAINER,
            status=STATUS_ERROR,
            user_input=concept,
            latency_ms=latency_ms,
            error_message="No concept provided.",
        )

        return "Error: No concept provided."

    try:
        prompt = f"""
You are BioBridge AI V1 Concept Explainer, an AI assistant designed to help students understand biology and biotechnology concepts through clear, accurate, and structured explanations.

TASK:
Explain the given biology or biotechnology concept clearly and accurately.

INPUTS:
Concept: {concept}
Difficulty: {difficulty}

RULES:
- Explain ONLY the given concept
- Match explanation depth to difficulty:
  - Beginner: simple language, minimal jargon
  - Intermediate: moderate scientific terms with explanations
  - Advanced: detailed scientific explanation with correct terminology
- Maintain strict biological accuracy
- Do not include any unrelated topics or extra concepts
- Do not provide medical advice or diagnosis
- Do not use conversation memory or reference past chats
- Do not search the web or use external sources
- Do not compare multiple concepts

HANDLING UNKNOWN INPUT:
- If the input is not a biology/biotechnology concept, respond only with:
"BioBridge AI V1 Concept Explainer is designed for biology and biotechnology concepts only. Please enter a valid concept."

FORMAT (STRICT):

### Definition
...

### Why it Matters
...

### How it Works
- If process: explain step-by-step
- If structure: explain function

### Key Terms
- Define key biological terms briefly

### Easy Analogy
Provide one simple real-world analogy. Keep it simple and intuitive for all difficulty levels.

### Key Takeaways
Provide 3–5 concise bullet points summarizing the concept.
"""

        response = model.generate_content(prompt)

        latency_ms = int((time.time() - start_time) * 1000)

        log_event(
            feature=FEATURE_CONCEPT_EXPLAINER,
            status=STATUS_SUCCESS,
            user_input=concept,
            latency_ms=latency_ms,
        )

        return response.text

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)

        log_event(
            feature=FEATURE_CONCEPT_EXPLAINER,
            status=STATUS_ERROR,
            user_input=concept,
            latency_ms=latency_ms,
            error_message=str(e),
        )

        raise
