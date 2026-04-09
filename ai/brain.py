from ai.agents.github import get_repo
from ai.agents.code_reader import build_code_context
from ai.agents.web_research import web_search
from ai.agents.local_reader import read_local_project
from ai.agents.infra import run_command
from ai.config import LIMITS

# 🔥 Logging
from ai.logger import log_error

# 🔥 Plugins
from ai.plugins.loader import load_plugins

PLUGINS = load_plugins()


# ===== INTENT DETECTION (IMPROVED) =====
def detect_intent(user_input):
    text = user_input.lower()

    infra_keywords = [
        "azure", "az", "subscription", "vm",
        "account", "tenant", "resource group"
    ]

    local_keywords = ["project", "code", "local"]

    return {
        "local": any(k in text for k in local_keywords),

        # 🔥 FIX: better infra detection
        "infra": any(k in text for k in infra_keywords),

        "repo": "/" in user_input,

        # web only if nothing else matches
        "web": not any(k in text for k in (
            infra_keywords + local_keywords + ["/"]
        ))
    }


# ===== REPO PARSER =====
def extract_repo(user_input):
    for w in user_input.split():
        if "/" in w:
            p = w.split("/")
            if len(p) == 2 and all(p):
                return p[0], p[1]
    return None, None


# ===== MAIN THINK FUNCTION =====
def think(user_input):

    intent = detect_intent(user_input)

    errors = []

    # =====================================================
    # 🔥 INFRA (DIRECT EXECUTION — NO LLM)
    # =====================================================
    if intent["infra"]:
        try:
            output = run_command("az account show")

            # 🔥 RAW OUTPUT → no hallucination
            return f"RAW_OUTPUT::{output}", "⚡ AGENT MODE (infra)"

        except Exception as e:
            log_error("INFRA", str(e))
            return "RAW_OUTPUT::[INFRA ERROR]", "⚡ AGENT MODE (infra)"

    local_data = ""
    repo_data = ""
    web_data = ""

    # =====================================================
    # LOCAL
    # =====================================================
    if intent["local"]:
        try:
            raw = read_local_project(".")
            local_data = raw[:LIMITS.get("LOCAL_MAX_CHARS", 5000)]
        except Exception as e:
            log_error("LOCAL", str(e))
            local_data = "[LOCAL ERROR]"
            errors.append("LOCAL ERROR")

    # =====================================================
    # REPO
    # =====================================================
    if intent["repo"]:
        owner, repo = extract_repo(user_input)

        if owner and repo:
            try:
                if get_repo(owner, repo):
                    repo_data = build_code_context(owner, repo)[
                        :LIMITS.get("REPO_MAX_CHARS", 4000)
                    ]
                else:
                    errors.append("REPO NOT FOUND")
            except Exception as e:
                log_error("REPO", str(e))
                errors.append("REPO ERROR")
        else:
            errors.append("INVALID REPO FORMAT")

    # =====================================================
    # WEB (ONLY IF NOTHING ELSE MATCHES)
    # =====================================================
    if intent["web"] and not (local_data or repo_data):
        try:
            web_data = web_search(user_input)[
                :LIMITS.get("WEB_MAX_CHARS", 1500)
            ]
        except Exception as e:
            log_error("WEB", str(e))
            errors.append("WEB ERROR")

    # =====================================================
    # FAIL-SAFE
    # =====================================================
    if intent["local"] and not local_data:
        local_data = "[LOCAL ERROR] No readable project data"

    # =====================================================
    # CONTEXT BUILD
    # =====================================================
    context = f"""
LOCAL:
{local_data}

REPO:
{repo_data}

WEB:
{web_data}

ERRORS:
{chr(10).join(errors) if errors else "None"}
"""

    # =====================================================
    # 🔥 PLUGIN HOOK (SAFE)
    # =====================================================
    for plugin in PLUGINS:
        try:
            result = plugin.run(user_input)

            if result:
                context += f"\nPLUGIN OUTPUT ({plugin.name}):\n{result}\n"

        except Exception as e:
            log_error(plugin.name, str(e))
            context += f"\n[PLUGIN ERROR - {plugin.name}]\n"

    # =====================================================
    # FINAL PROMPT
    # =====================================================
    prompt = f"""
You are a senior DevOps engineer.

STRICT RULES:
- DO NOT explain system behavior
- DO NOT describe how the system works
- ONLY analyze real data
- COMPLETE ALL sections fully

TASK:
1. What this project/system is
2. Key components
3. Issues / risks
4. Improvements / next steps

{context}

User:
{user_input}
"""

    return prompt, "⚡ AGENT MODE"