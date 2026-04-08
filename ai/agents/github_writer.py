import requests
import os
from dotenv import load_dotenv
from pathlib import Path
import base64

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

BASE_URL = "https://api.github.com"


def headers():
    return {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }


# ===== GET DEFAULT BRANCH SHA =====
def get_main_sha(owner, repo):
    url = f"{BASE_URL}/repos/{owner}/{repo}/git/ref/heads/main"
    res = requests.get(url, headers=headers())
    return res.json()["object"]["sha"]


# ===== CREATE BRANCH =====
def create_branch(owner, repo, branch_name):
    sha = get_main_sha(owner, repo)

    url = f"{BASE_URL}/repos/{owner}/{repo}/git/refs"

    payload = {
        "ref": f"refs/heads/{branch_name}",
        "sha": sha
    }

    res = requests.post(url, json=payload, headers=headers())

    return res.status_code == 201


# ===== GET FILE =====
def get_file(owner, repo, path):
    url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}"
    res = requests.get(url, headers=headers())

    if res.status_code != 200:
        return None, None

    data = res.json()

    content = base64.b64decode(data["content"]).decode("utf-8")
    sha = data["sha"]

    return content, sha


# ===== UPDATE FILE =====
def update_file(owner, repo, path, content, branch, sha):
    url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}"

    payload = {
        "message": f"update {path}",
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch,
        "sha": sha
    }

    res = requests.put(url, json=payload, headers=headers())

    return res.status_code in [200, 201]


# ===== CREATE PR =====
def create_pr(owner, repo, branch):
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"

    payload = {
        "title": f"{branch}: Automated Update",
        "head": branch,
        "base": "main",
        "body": "Automated changes by AI system"
    }

    res = requests.post(url, json=payload, headers=headers())

    return res.json().get("html_url")

# ===== LIST FILES =====
def list_repo_files(owner, repo):
    import requests, os

    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"

    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }

    res = requests.get(url, headers=headers)

    files = []

    for item in res.json().get("tree", []):
        if item["type"] == "blob":
            files.append(item["path"])

    return files