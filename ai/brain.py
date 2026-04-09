import re

from ai.agents.github import get_repo
from ai.agents.code_reader import build_code_context
from ai.agents.web_research import web_search
from ai.agents.local_reader import read_local_project
from ai.agents.infra import run_command
from ai.config import LIMITS
from ai.logger import log_error

_plugins_cache = None


def _get_plugins():
    global _plugins_cache
    if _plugins_cache is None:
        from ai.plugins.loader import load_plugins
        _plugins_cache = load_plugins()
    return _plugins_cache


INFRA_KEYWORDS = [
    "azure", "az ", "subscription", "resource group",
    "account", "tenant",
]

LOCAL_KEYWORDS = ["project", "code", "local"]


def detect_intent(user_input):
    text = user_input.lower()

    # word-boundary check for "vm" to avoid JVM/nvim false positives
    has_vm = bool(re.search(r'\bvm\b', text))
    has_infra = any(k in text for k in INFRA_KEYWORDS) or has_vm

    # repo: only if a valid owner/repo pair is parseable
    owner, repo = extract_repo(user_input)
    has_repo = owner is not None and repo is not None

    has_local = any(k in text for k in LOCAL_KEYWORDS)

    has_web = not (has_infra or has_local or has_repo)

    return {
        "local": has_local,
        "infra": has_infra,
        "repo": has_repo,
        "web": has_web,
    }


def extract_repo(user_input):
    for w in user_input.split():
        if "/" in w:
            p = w.split("/")
            if len(p) == 2 and all(p) and not w.startswith("http"):
                return p[0], p[1]
    return None, None


def _build_prompt(user_input, context, intent):
    if intent["local"]:
        system = (
            "You are a senior software engineer doing a code review.\n"
            "Focus on: code quality, bugs, security issues, and concrete improvements.\n"
            "Be specific — reference file names and line numbers where possible."
        )
    elif intent["repo"]:
        system = (
            "You are a senior engineer reviewing a GitHub repository.\n"
            "Focus on: architecture, dependencies, risks, and suggested next steps.\n"
            "Be concise and actionable."
        )
    elif intent["web"]:
        system = (
            "You are a technical researcher synthesizing web search results.\n"
            "Answer the user's question directly using the provided sources.\n"
            "Cite sources where relevant. Be accurate — do not hallucinate."
        )
    else:
        system = (
            "You are a senior DevOps engineer.\n"
            "Analyze the provided data and answer the user's question directly.\n"
            "Be specific and actionable."
        )

    return f"""{system}

STRICT RULES:
- Only analyze the real data provided below
- Do not describe how the system works unless asked
- Do not repeat the user's question back to them

CONTEXT:
{context}

USER QUESTION:
{user_input}
"""


def think(user_input):

    intent = detect_intent(user_input)
    errors = []

    # =====================================================
    # INFRA (DIRECT EXECUTION — NO LLM)
    # =====================================================
    if intent["infra"]:
        try:
            output = run_command("az account show")
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
    # WEB (only if nothing else matched)
    # =====================================================
    if intent["web"] and not (local_data or repo_data):
        try:
            web_data = web_search(user_input)[
                :LIMITS.get("WEB_MAX_CHARS", 1500)
            ]
        except Exception as e:
            log_error("WEB", str(e))
            errors.append("WEB ERROR")

    if intent["local"] and not local_data:
        local_data = "[LOCAL ERROR] No readable project data"

    # =====================================================
    # CONTEXT BUILD
    # =====================================================
    context = f"""LOCAL:
{local_data}

REPO:
{repo_data}

WEB:
{web_data}

ERRORS:
{chr(10).join(errors) if errors else "None"}
"""

    # =====================================================
    # PLUGIN HOOK (SAFE, LAZY-LOADED)
    # =====================================================
    for plugin in _get_plugins():
        try:
            result = plugin.run(user_input)
            if result:
                context += f"\nPLUGIN OUTPUT ({plugin.name}):\n{result}\n"
        except Exception as e:
            log_error(plugin.name, str(e))
            context += f"\n[PLUGIN ERROR - {plugin.name}]\n"

    prompt = _build_prompt(user_input, context, intent)
    return prompt, "⚡ AGENT MODE"
