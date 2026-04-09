import requests
from ai.config import GITHUB_TOKEN

# 🔥 RESTORE CONSTANT (FIX)
BASE_URL = "https://api.github.com"


# 🔥 SAFE REQUEST (COMPATIBLE)
def safe_request(method, url, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    headers["Accept"] = "application/vnd.github+json"

    try:
        r = requests.request(method, url, headers=headers, **kwargs)

        if r.status_code >= 400:
            return None, f"{r.status_code}: {r.text}"

        # Some endpoints return empty body
        try:
            return r.json(), None
        except:
            return {}, None

    except Exception as e:
        return None, str(e)


# 🔥 AUTH VALIDATION
def validate_github():
    if not GITHUB_TOKEN:
        return False, "Missing GITHUB_TOKEN"

    data, err = safe_request("GET", f"{BASE_URL}/user")

    if err:
        return False, err

    return True, "OK"


# 🔥 REPO FETCH
def get_repo(owner, repo):
    ok, _ = validate_github()

    if not ok:
        return None

    data, err = safe_request(
        "GET",
        f"{BASE_URL}/repos/{owner}/{repo}"
    )

    if err:
        return None

    return data