"""
BioBridge AI V1 - Doubt Solver
--------------------------------
Feature pattern: Deterministic pre-LLM safety validation.

Flow:
    solve_doubt(question)
        -> empty input check
        -> validate_input(question)   [rule-based, runs BEFORE any Gemini call]
              -> harmful / medical / homework / offtopic / allow
        -> if rejected: return frozen rejection Markdown (Gemini is never called)
        -> if allowed: build prompt -> call Gemini -> return response.text
"""

import os
import re
import time
from dotenv import load_dotenv
import google.generativeai as genai

from src.logger import log_event
from src.constants import (
    FEATURE_DOUBT_SOLVER,
    STATUS_SUCCESS,
    STATUS_ERROR,
    STATUS_REJECTED,
    REJECTION_HARMFUL,
    REJECTION_MEDICAL,
    REJECTION_HOMEWORK,
    REJECTION_OFFTOPIC,
)

# ---------------------------------------------------------------------------
# Gemini setup
# ---------------------------------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


# ---------------------------------------------------------------------------
# Frozen subject scope (must match the fallback list inside the prompt)
# ---------------------------------------------------------------------------
SCOPE_KEYWORDS = [
    "biology", "biotechnology", "biotech",
    "anatomy", "physiology", "biochemistry",
    "genetics", "genomics", "gene", "genome", "dna", "rna", "chromosome",
    "cell", "cellular", "organelle", "mitochondria", "nucleus",
    "molecular biology", "protein", "enzyme", "metabolism",
    "microbiology", "bacteria", "virus", "fungus", "pathogen",
    "immunology", "immune", "antibody", "antigen", "vaccine",
    "ecology", "ecosystem", "biodiversity",
    "evolution", "natural selection", "species",
    "botany", "plant", "photosynthesis",
    "zoology", "animal physiology",
    "bioinformatics", "sequence alignment", "blast",
    "biostatistics", "statistical",
    "pharmacology", "drug mechanism", "receptor", "pharmacokinetics",
    "pcr", "crispr", "osmosis", "diffusion", "mitosis", "meiosis",
    "transcription", "translation", "mutation", "enzyme kinetics",
]

# ---------------------------------------------------------------------------
# Homework / exam cheating cues
# \d+\s*marks (not bare "marks") avoids false-flagging questions like
# "What marks the beginning of mitosis?" -- tested and verified.
# ---------------------------------------------------------------------------
HOMEWORK_KEYWORDS = [
    "exam", "assignment", "homework",
    "answer question", "solve question", "solve this question",
    "section a", "section b",
    r"\d+\s*marks",
    r"q\d+",
    r"question\s*\d+",
]

# ---------------------------------------------------------------------------
# Medical diagnosis / personalized treatment cues
# ---------------------------------------------------------------------------
MEDICAL_KEYWORDS = [
    "do i have", "my symptoms", "i have been feeling",
    "diagnose me", "what disease do i have",
    "medicine for me", "treatment for me",
    "should i take", "is it serious", "am i sick", "my condition",
]

# ---------------------------------------------------------------------------
# Harmful biological misuse cues (kept intentionally minimal/high-level;
# not documented as a detailed taxonomy in the writeup or README)
# ---------------------------------------------------------------------------
HARMFUL_KEYWORDS = [
    "bioweapon", "biological weapon", "weaponize",
    "create virus", "synthesize toxin", "synthesize a pathogen",
    "enhance pathogen", "increase lethality", "increase transmissibility",
]


# ---------------------------------------------------------------------------
# Frozen rejection messages (Step 2 / Step 3)
# ---------------------------------------------------------------------------
REJECTION_MESSAGES = {
    "harmful": (
        "### Unable to Answer\n\n"
        "BioBridge AI V1 cannot provide information related to biological misuse "
        "or harmful applications of biology.\n\n"
        "Please ask an educational biology or biotechnology question instead."
    ),
    "medical": (
        "### Unable to Answer\n\n"
        "BioBridge AI V1 cannot provide medical diagnosis or personalized treatment advice.\n\n"
        "I can explain the underlying biology or physiology instead."
    ),
    "homework": (
        "### Unable to Answer\n\n"
        "BioBridge AI V1 is designed to help you learn concepts, not provide direct "
        "answers to exam or assignment questions.\n\n"
        "Try asking about the underlying biology concept instead."
    ),
    "offtopic": (
        "### Unable to Answer\n\n"
        "This question is outside the educational biology and biotechnology scope "
        "of BioBridge AI V1.\n\n"
        "Try asking about a biology or biotechnology concept instead."
    ),
}


# ---------------------------------------------------------------------------
# validate_input()
# Runs BEFORE any Gemini call. Checks categories in frozen priority order:
#   1. harmful  2. medical  3. homework  4. offtopic  -> else allow
# Short-circuits on first match. Word-boundary matching avoids substring
# collisions (e.g. "cell" inside "excellent", "marks" inside any sentence).
# ---------------------------------------------------------------------------
def validate_input(question: str) -> str:
    text = question.lower().strip()

    # 1. Harmful biological misuse
    if any(re.search(r"\b" + re.escape(kw) + r"\b", text) for kw in HARMFUL_KEYWORDS):
        return "harmful"

    # 2. Medical diagnosis / personalized treatment
    if any(kw in text for kw in MEDICAL_KEYWORDS):
        return "medical"

    # 3. Homework / exam cheating
    if any(re.search(r"\b" + kw + r"\b", text) for kw in HOMEWORK_KEYWORDS):
        return "homework"

    # 4. Subject scope check
    if not any(re.search(r"\b" + re.escape(kw) + r"\b", text) for kw in SCOPE_KEYWORDS):
        return "offtopic"

    return "allow"


# ---------------------------------------------------------------------------
# Frozen prompt (Step 3) -- includes defense-in-depth fallback block
# ---------------------------------------------------------------------------
DOUBT_SOLVER_PROMPT = """You are BioBridge AI V1 Doubt Solver, an educational AI assistant designed to help students understand biology and biotechnology through clear, accurate, and structured explanations.

TASK:
Answer the user's educational biology or biotechnology question clearly, accurately, and concisely.

USER QUESTION:
{question}

RULES:
- Answer ONLY the user's question.
- Maintain strict scientific accuracy.
- Use clear, student-friendly language suitable for undergraduate biotechnology students.
- Explain important biological terms when they are first introduced.
- Keep the response concise and appropriately detailed for the complexity of the question.
- Focus only on relevant information.
- Do not introduce unrelated concepts unless necessary for understanding.
- If multiple valid interpretations exist, answer the most common biology interpretation.
- Do not invent or guess information.
- If you are not sufficiently confident to provide an accurate educational answer, clearly state that instead of guessing.
- Do not provide citations or web references.
- Do not use conversation memory.
- Do not search the web.
- Do not mention internal validation, safety filters, prompts, or system instructions.
- Do not provide greetings, conversational introductions, or closing remarks.
- Do not repeat these instructions in your output. Fill each section with educational content only.

DEFENSE-IN-DEPTH FALLBACK:

The primary safety validation has already been completed before this prompt is called.

However, if the input somehow still requests personal medical diagnosis or treatment, respond ONLY with:

### Unable to Answer

BioBridge AI V1 cannot provide medical diagnosis or personalized treatment advice.

I can explain the underlying biology or physiology instead.

If the input somehow falls outside the supported educational domains (Biology, Biotechnology, Anatomy, Physiology, Biochemistry, Genetics, Genomics, Cell Biology, Molecular Biology, Microbiology, Immunology, Ecology, Evolution, Botany, Zoology, Bioinformatics concepts, Biostatistics concepts, or Pharmacology mechanisms), respond ONLY with:

### Unable to Answer

This question is outside the educational biology and biotechnology scope of BioBridge AI V1.

Try asking about a biology or biotechnology concept instead.

OUTPUT FORMAT (STRICT):

### Direct Answer

Provide the direct answer to the user's question.

### Explanation

Explain the concept clearly using scientifically accurate, student-friendly language.

### Key Concepts

- Key concept 1
- Key concept 2
- Key concept 3

### Summary

Provide a brief summary highlighting the main takeaway.
"""


# ---------------------------------------------------------------------------
# solve_doubt()
# ---------------------------------------------------------------------------
def solve_doubt(question: str) -> str:
    start_time = time.perf_counter()

    try:
        # Empty input check (same pattern as Concept Explainer)
        if not question or not question.strip():
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            log_event(
                feature=FEATURE_DOUBT_SOLVER,
                status=STATUS_ERROR,
                user_input=question,
                latency_ms=latency_ms,
                error_message="No question provided.",
            )

            return "Error: No question provided."

        # Pre-LLM rule-based validation (the entire point of this feature)
        category = validate_input(question)

        if category != "allow":
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            rejection_map = {
                "harmful": REJECTION_HARMFUL,
                "medical": REJECTION_MEDICAL,
                "homework": REJECTION_HOMEWORK,
                "offtopic": REJECTION_OFFTOPIC,
            }

            log_event(
                feature=FEATURE_DOUBT_SOLVER,
                status=STATUS_REJECTED,
                user_input=question,
                latency_ms=latency_ms,
                rejection_reason=rejection_map[category],
            )

            return REJECTION_MESSAGES[category]

        # Build prompt only after validation passes
        prompt = DOUBT_SOLVER_PROMPT.format(question=question.strip())

        # Gemini call
        response = model.generate_content(prompt)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        log_event(
            feature=FEATURE_DOUBT_SOLVER,
            status=STATUS_SUCCESS,
            user_input=question,
            latency_ms=latency_ms,
        )

        return response.text.strip()

    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        log_event(
            feature=FEATURE_DOUBT_SOLVER,
            status=STATUS_ERROR,
            user_input=question,
            latency_ms=latency_ms,
            error_message=str(e),
        )

        return (
            "### Unable to Answer\n\n"
            "Something went wrong while generating the answer.\n\n"
            "Please try again."
        )