import anthropic
import time

from ai.brain import think
from ai.memory import search_memory, save_memory
from ai.config import ANTHROPIC_API_KEY, MODELS, LIMITS

from ai.agents.github_writer import (
    create_branch,
    update_file,
    create_pr,
    get_file,
    list_repo_files
)

from ai.agents.diff_engine import get_local_file_map, compare_maps
from ai.agents.pr_analyzer import summarize_changes, risk_score


BLOCKED = [
    ".env",
    "memory.json",
    "session.json",
    "memory_store/",
    "sessions/",
    "__pycache__",
]


def is_blocked(path):
    return any(b in path for b in BLOCKED)


def claude(prompt):

    errors = []

    for model in MODELS:
        model = model.strip()  # 🔥 fix hidden whitespace

        try:
            print(f"[DEBUG] Using model: {model}")

            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

            res = client.messages.create(
                model=model,
                max_tokens=LIMITS["MODEL_MAX_TOKENS"],
                messages=[{"role": "user", "content": prompt}]
            )

            return res.content[0].text

        except Exception as e:
            errors.append(f"{model}: {str(e)}")

    return "[MODEL ERROR]\n" + "\n".join(errors)


def extract_repo(user_input):
    for w in user_input.split():
        if "/" in w:
            p = w.split("/")
            if len(p) == 2:
                return p[0], p[1]
    return None, None


def is_pr_request(text):
    return any(k in text for k in ["create pr", "sync repo", "push repo"])


def ask_approval():
    print("\n⚠️ Approve PR? (y/n): ", end="")
    return input().strip().lower() == "y"


# 🔥 THIS WAS MISSING (CRITICAL)
def run_model_core(mode, user_input):

    mem = search_memory(user_input)
    if mem:
        print("⚠️ Memory found")

    text = user_input.lower()

    # =====================================================
    # PR FLOW
    # =====================================================
    if is_pr_request(text):

        owner, repo = extract_repo(user_input)

        if not repo:
            return "❌ Repo not detected"

        try:
            local_map = get_local_file_map()
            repo_files = list_repo_files(owner, repo)

            repo_map = {}
            for f in repo_files:
                content, _ = get_file(owner, repo, f)
                if content:
                    repo_map[f] = content

            changes = compare_maps(local_map, repo_map)

            # 🔥 filter blocked
            changes = [c for c in changes if not is_blocked(c["path"])]

            if not changes:
                return "✅ Repo already up to date"

            preview = summarize_changes(changes)
            risk = risk_score(changes)

            print(f"""
================ PR PREVIEW ================

{preview}

------------------------------------------
RISK LEVEL: {risk}

==========================================
""")

            if not ask_approval():
                return "❌ PR Cancelled"

            branch = f"ai-sync-{int(time.time())}"
            create_branch(owner, repo, branch)

            updated = []

            for c in changes:
                path = c["path"]
                content = c["content"]

                try:
                    _, sha = get_file(owner, repo, path)
                    update_file(owner, repo, path, content, branch, sha)
                except:
                    update_file(owner, repo, path, content, branch, None)

                updated.append(path)

            pr_url = create_pr(owner, repo, branch)

            save_memory({
                "issue": user_input,
                "solution": f"PR created with {len(updated)} files"
            })

            return f"""
================ AI SYSTEM ================

MODE:
🚀 PR EXECUTED

------------------------------------------

Files changed: {len(updated)}
Risk: {risk}
PR: {pr_url}

==========================================
"""

        except Exception as e:
            return f"[PR ERROR] {e}"

    # =====================================================
    # NORMAL FLOW
    # =====================================================
    prompt, status = think(user_input)

    if prompt.startswith("RAW_OUTPUT::"):
        return prompt.replace("RAW_OUTPUT::", "")

    result = claude(prompt)

    save_memory({
        "issue": user_input,
        "solution": result
    })

    return f"""
================ AI SYSTEM ================

MODE:
{status}

------------------------------------------

{result}

==========================================
"""