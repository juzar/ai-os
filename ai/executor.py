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


# ===== LLM =====
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

    return "[ERROR] All models failed"


# ===== REPO PARSER =====
def extract_repo(user_input):
    for w in user_input.split():
        if "/" in w:
            p = w.split("/")
            if len(p) == 2 and all(p):
                return p[0], p[1]
    return None, None


# ===== 🔥 EXECUTION DETECTOR (NEW) =====
def is_pr_request(text):
    keywords = ["create pr", "sync repo", "push repo", "sync up"]
    return any(k in text for k in keywords)


# ===== MAIN =====
def run_model(mode, user_input):

    mem = search_memory(user_input)
    if mem:
        print("⚠️ Memory found")

    text = user_input.lower()

    # =====================================================
    # 🚀 FORCE PR EXECUTION (FIX)
    # =====================================================
    if is_pr_request(text):

        owner, repo = extract_repo(user_input)

        if not repo:
            return "❌ Repo not detected (use owner/repo)"

        try:
            # LOCAL
            local_map = get_local_file_map()

            # REMOTE
            repo_files = list_repo_files(owner, repo)

            repo_map = {}

            for f in repo_files:
                content, _ = get_file(owner, repo, f)
                if content:
                    repo_map[f] = content

            # DIFF
            changes = compare_maps(local_map, repo_map)

            if not changes:
                return "✅ Repo already up to date"

            branch = f"ai-sync-{int(time.time())}"
            create_branch(owner, repo, branch)

            new_files = []
            modified_files = []

            for change in changes:

                path = change["path"]
                content = change["content"]

                try:
                    _, sha = get_file(owner, repo, path)

                    update_file(owner, repo, path, content, branch, sha)
                    modified_files.append(path)

                except:
                    update_file(owner, repo, path, content, branch, None)
                    new_files.append(path)

            pr_url = create_pr(owner, repo, branch)

            return f"""
================ AI SYSTEM ================

MODE:
🚀 FULL REPO SYNC

------------------------------------------

🆕 New files:
{chr(10).join(new_files) if new_files else "None"}

✏️ Modified files:
{chr(10).join(modified_files) if modified_files else "None"}

🌿 Branch: {branch}
🔗 PR: {pr_url}

==========================================
"""

        except Exception as e:
            return f"[SYNC ERROR] {e}"

    # =====================================================
    # NORMAL FLOW (UNCHANGED)
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