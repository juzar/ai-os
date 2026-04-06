```python
# FILE: ai/brain.py
from ai.agents.github import get_repo
from ai.agents.code_reader import build_code_context
from ai.agents.web_research import web_search
from ai.agents.local_reader import read_local_project
from ai.agents.infra import run
from ai.config import LIMITS


def detect_intent(user_input):
    text = user_input.lower()

    return {
        "local": any(k in text for k in ["project", "code", "local"]),
        "repo": "/" in user_input,
        "infra": any(k in text for k in ["azure", "az", "subscription", "vm"]),
        "web": True
    }


def extract_repo(user_input):
    for w in user_input.split():
        if "/" in w:
            p = w.split("/")
            if len(p) == 2:
                return p[0], p[1]
    return None, None


def think(user_input):

    intent = detect_intent(user_input)

    # ===== INFRA (NO LLM) =====
    if intent["infra"]:
        output = run("az account show")
        return f"RAW_OUTPUT::{output}", "⚡ AGENT MODE (infra)"

    local_data = ""
    repo_data = ""
    web_data = ""

    # ===== LOCAL =====
    if intent["local"]:
        try:
            local_data = read_local_project(".")[:LIMITS["LOCAL_MAX_CHARS"]]
        except Exception as e:
            local