"""Project configuration."""

from pathlib import Path
from dotenv import load_dotenv
import os


# =========================
# Project Root
# =========================
load_dotenv()

# LLM Configuration
LLM_API_KEY= os.getenv('LLM_API_KEY')

# Optional LLM settings
LLM_MODEL=os.getenv('LLM_MODEL')
LLM_BASE_URL=os.getenv('LLM_BASE_URL')


BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Chunking Parameters
# =========================

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 150

# =========================
# Data Paths
# =========================

DATA_DIR = BASE_DIR / "data"

DOCUMENTS_DIR = DATA_DIR / "documents"

EVALUATION_DIR = DATA_DIR / "evaluation"

METADATA_FILE = DATA_DIR / "metadata.json"

QUESTIONS_FILE = EVALUATION_DIR / "questions.json"


# =========================
# Vector Store
# =========================

VECTORSTORE_DIR = BASE_DIR / "vector_store"


# =========================
# Environment
# =========================

ENV_FILE = BASE_DIR / ".env"