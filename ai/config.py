import os
from dotenv import load_dotenv

load_dotenv()

# ================================
# 🔑 API KEYS (SAFE LOAD)
# ================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 🔥 VALIDATION (FAIL FAST)
if not ANTHROPIC_API_KEY:
    raise ValueError("❌ Missing ANTHROPIC_API_KEY in .env")

# Optional but recommended
if not GITHUB_TOKEN:
    print("⚠️ Warning: GITHUB_TOKEN not set (GitHub features may fail)")

# 🔥 CLEAN STRINGS (avoid hidden bugs)
ANTHROPIC_API_KEY = ANTHROPIC_API_KEY.strip()
if GITHUB_TOKEN:
    GITHUB_TOKEN = GITHUB_TOKEN.strip()

# ================================
# 🤖 MODELS
# ================================

MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6"
]

# ================================
# ⚙️ LIMITS
# ================================

LIMITS = {
    "MODEL_MAX_TOKENS": int(os.getenv("MODEL_MAX_TOKENS", 1000)),
    "LOCAL_MAX_CHARS": 4000,
    "REPO_MAX_CHARS": 3000,
    "WEB_MAX_CHARS": 1500
}