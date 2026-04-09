import json
import time
from pathlib import Path

MEMORY_FILE = Path("memory.json")
MAX_ITEMS = 200


def load_memory():
    if not MEMORY_FILE.exists():
        return []

    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)

            fixed = []
            now = time.time()

            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    continue
                if "timestamp" not in item:
                    item["timestamp"] = now - i
                fixed.append(item)

            return fixed

    except:
        return []


def save_memory(entry):
    data = load_memory()

    entry["timestamp"] = time.time()
    data.append(entry)

    data = sorted(
        data,
        key=lambda x: x.get("timestamp", 0),
        reverse=True
    )[:MAX_ITEMS]

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def search_memory(query):
    data = load_memory()
    words = [w for w in query.lower().split() if len(w) > 2]

    if not words:
        return []

    scored = []
    for item in data:
        issue = item.get("issue", "").lower()
        score = sum(1 for w in words if w in issue)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:3]]
