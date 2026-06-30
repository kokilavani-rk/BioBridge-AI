"""
BioBridge AI V1 - Shared Constants
----------------------------------
Central location for shared constants used across the project.
"""

# ==========================================
# Logging Configuration
# ==========================================

LOG_DIRECTORY = "logs"
LOG_FILENAME = "biobridge_log.jsonl"
MAX_LOG_INPUT_LENGTH = 200


# ==========================================
# Feature Names
# ==========================================

FEATURE_MNEMONIC = "mnemonic"
FEATURE_CONCEPT_EXPLAINER = "concept_explainer"
FEATURE_QUIZ_GENERATOR = "quiz_generator"
FEATURE_DOUBT_SOLVER = "doubt_solver"


# ==========================================
# Log Status Values
# ==========================================

STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
STATUS_REJECTED = "rejected"


# ==========================================
# Rejection Reasons
# ==========================================

REJECTION_HARMFUL = "harmful"
REJECTION_MEDICAL = "medical"
REJECTION_HOMEWORK = "homework"
REJECTION_OFFTOPIC = "offtopic"