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


# 🚫 BLOCKED FILES (CRITICAL)
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
    for model in MODELS:
        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

            res = client.messages.create(
                model=model,
                max_tokens=LIMITS["MODEL_MAX_TOKENS"],
                messages=[{"role": "user", "content": prompt}]
            )

            return res.content[0].text

        except Exception:
            continue

    return "[ERROR] Model failed"


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


def run_model(mode, user_input):

    mem = search_memory(user_input)
    if mem:
        print("⚠️ Memory found")

    text = user_input.lower()

    # =====================================================
    # 🚀 NEW PR FLOW (ONLY FLOW — OLD REMOVED)
    # =====================================================
    if is_pr_request(text):

        owner, repo = extract_repo(user_input)

        if not repo:
            return "❌ Repo not detected"

        try:
            # LOAD
            local_map = get_local_file_map()
            repo_files = list_repo_files(owner, repo)

            repo_map = {}
            for f in repo_files:
                content, _ = get_file(owner, repo, f)
                if content:
                    repo_map[f] = content

            # DIFF
            changes = compare_maps(local_map, repo_map)

            # 🔥 FILTER BLOCKED FILES
            changes = [c for c in changes if not is_blocked(c["path"])]

            if not changes:
                return "✅ Repo already up to date"

            # 🔥 PREVIEW
            preview = summarize_changes(changes)
            risk = risk_score(changes)

            print(f"""
================ PR PREVIEW ================

{preview}

------------------------------------------
RISK LEVEL: {risk}

==========================================
""")

            # 🔥 APPROVAL
            if not ask_approval():
                return "❌ PR Cancelled"

            # EXECUTE
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
🚀 PR EXECUTED (SAFE)

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