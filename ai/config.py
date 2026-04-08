from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-3-haiku-20240307"
]

LIMITS = {
    "MODEL_MAX_TOKENS": int(os.getenv("MODEL_MAX_TOKENS", 400))
}