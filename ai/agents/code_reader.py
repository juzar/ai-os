import requests
from ai.agents.github import safe_request, BASE_URL


# ===== GET REPO FILE TREE =====
def get_repo_tree(owner, repo):
    url = f"{BASE_URL}/repos/{owner}/{repo}/git/trees/main?recursive=1"

    res = safe_request("GET", url)

    if res.status_code != 200:
        return []

    data = res.json()

    return [f["path"] for f in data.get("tree", []) if f["type"] == "blob"]


# ===== PICK IMPORTANT FILES =====
def select_relevant_files(files):
    important = []

    for f in files:
        if any(x in f.lower() for x in [
            "readme", "main", "app", "server",
            "index", "api", ".py", ".js", ".ts"
        ]):
            important.append(f)

    return important[:5]  # 🔥 token control


# ===== READ FILE CONTENT =====
def get_file_content(owner, repo, path):
    url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}"

    res = safe_request("GET", url)

    if res.status_code != 200:
        return ""

    import base64
    data = res.json()

    content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")

    return content[:2000]  # 🔥 token limit


# ===== BUILD CODE CONTEXT =====
def build_code_context(owner, repo):
    files = get_repo_tree(owner, repo)

    selected = select_relevant_files(files)

    context = ""

    for f in selected:
        content = get_file_content(owner, repo, f)

        context += f"\nFILE: {f}\n{content}\n"

    return context[:6000]  # hard cap