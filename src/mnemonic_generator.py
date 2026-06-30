"""
BioBridge AI - Mnemonic Generator (V1)
----------------------------------------
Takes a biology topic or list of terms and returns a structured,
student-friendly mnemonic using the Gemini API.
"""

import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

from src.logger import log_event
from src.constants import (
    FEATURE_MNEMONIC,
    STATUS_SUCCESS,
    STATUS_ERROR,
)

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_mnemonic(topic):
    start_time = time.time()

    try:
        prompt = f"""
You are BioBridge AI, a biology study assistant that creates mnemonics for students.

TASK:
Generate ONE clear, accurate, and memorable mnemonic for the given biology topic.

TOPIC:
{topic}

RULES:
- Use ONLY real English words (no fake or forced words)
- Keep mnemonic short, natural, and easy to remember
- Ensure biological accuracy
- If multiple biology terms are given, map each term in order clearly
- Do not include any conversational introductions, greetings, or conclusions.

IMPORTANT SAFETY RULE:
- If the input does NOT contain recognizable biology/anatomy/medical concepts, respond only with:
"I couldn't identify standard biology terms for this topic. Try being more specific."

COMPLETENESS RULE:
- If the topic refers to a standard biological system (e.g., cranial nerves, taxonomic ranks), include all standard terms without omission.

OUTPUT FORMAT (STRICT):

Mnemonic: <one line mnemonic>

Explanation:
- For each mnemonic word, provide:
  - The biology term it represents.
  - A one-line student-friendly biological definition or function (when applicable).
- Keep each explanation concise (one sentence).
"""

        response = model.generate_content(prompt)

        latency_ms = int((time.time() - start_time) * 1000)

        log_event(
            feature=FEATURE_MNEMONIC,
            status=STATUS_SUCCESS,
            user_input=topic,
            latency_ms=latency_ms,
        )

        return response.text

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)

        log_event(
            feature=FEATURE_MNEMONIC,
            status=STATUS_ERROR,
            user_input=topic,
            latency_ms=latency_ms,
            error_message=str(e),
        )

        raise