import requests
import os
from dotenv import load_dotenv
from pathlib import Path
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

BASE_URL = "https://api.github.com"


def get_headers():
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise Exception("❌ Missing GITHUB_TOKEN")

    return {
        "Authorization": f"Bearer {token.strip()}",
        "Accept": "application/vnd.github+json"
    }


# ===== SAFE REQUEST =====
def safe_request(method, url, payload=None):
    try:
        if method == "GET":
            return requests.get(url, headers=get_headers(), timeout=10)
        elif method == "POST":
            return requests.post(url, json=payload, headers=get_headers(), timeout=10)

    except requests.exceptions.SSLError:
        print("⚠️ SSL issue detected — retrying without verification")

        if method == "GET":
            return requests.get(url, headers=get_headers(), verify=False, timeout=10)
        elif method == "POST":
            return requests.post(url, json=payload, headers=get_headers(), verify=False, timeout=10)


# ===== DIRECT REPO CHECK (🔥 FIX) =====
def get_repo(owner, repo):
    url = f"{BASE_URL}/repos/{owner}/{repo}"

    res = safe_request("GET", url)

    if res.status_code == 200:
        return f"✅ Found repo: {owner}/{repo}"

    elif res.status_code == 404:
        return None

    else:
        return f"[GitHub Error] {res.status_code} - {res.text}"


# ===== SEARCH (FALLBACK ONLY) =====
def search_repo(repo_name, owner="juzar"):
    url = f"{BASE_URL}/search/repositories?q={repo_name}+user:{owner}"

    res = safe_request("GET", url)

    if res.status_code != 200:
        return None

    data = res.json()

    if not data.get("items"):
        return None

    return data["items"][0]["name"]


# ===== GET LATEST PR =====
def get_latest_pr(owner, repo):
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls?state=all&per_page=1"

    res = safe_request("GET", url)

    if res.status_code != 200:
        return f"[GitHub Error] {res.status_code} - {res.text}"

    data = res.json()

    if not data:
        return "No PR found"

    pr = data[0]

    return f"""
Latest PR:
Title: {pr['title']}
PR Number: {pr['number']}
Author: {pr['user']['login']}
State: {pr['state']}
URL: {pr['html_url']}
"""


# ===== GET SPECIFIC PR =====
def get_pr(owner, repo, pr_number):
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"

    res = safe_request("GET", url)

    if res.status_code != 200:
        return f"[GitHub Error] {res.status_code} - {res.text}"

    pr = res.json()

    return f"""
PR Details:
Title: {pr['title']}
Author: {pr['user']['login']}
Changes: +{pr['additions']} / -{pr['deletions']}
Files Changed: {pr['changed_files']}
URL: {pr['html_url']}
"""


# ===== CREATE BRANCH =====
def create_branch(owner, repo, branch_name):
    ref_url = f"{BASE_URL}/repos/{owner}/{repo}/git/ref/heads/main"

    ref = safe_request("GET", ref_url).json()
    sha = ref["object"]["sha"]

    create_url = f"{BASE_URL}/repos/{owner}/{repo}/git/refs"

    payload = {
        "ref": f"refs/heads/{branch_name}",
        "sha": sha
    }

    res = safe_request("POST", create_url, payload)

    return res.status_code == 201


# ===== CREATE PR =====
def create_pr(owner, repo, branch_name, title, body):
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"

    payload = {
        "title": title,
        "head": branch_name,
        "base": "main",
        "body": body
    }

    res = safe_request("POST", url, payload)

    return res.json()

# ===== LIST USER REPOS =====
def list_repos(owner):
    url = f"{BASE_URL}/users/{owner}/repos?per_page=50"

    res = safe_request("GET", url)

    if res.status_code != 200:
        return f"[GitHub Error] {res.status_code} - {res.text}"

    repos = res.json()

    if not repos:
        return "No repositories found"

    result = ""

    for r in repos[:20]:  # 🔥 limit for tokens
        result += f"- {r['name']} (⭐ {r['stargazers_count']})\n"

    return result