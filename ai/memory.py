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

            # 🔥 FIX: normalize all entries
            fixed = []
            now = time.time()

            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    continue

                # 🔥 ensure timestamp exists
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

    # 🔥 SAFE SORT (no crash)
    data = sorted(
        data,
        key=lambda x: x.get("timestamp", 0),
        reverse=True
    )[:MAX_ITEMS]

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def search_memory(query):
    data = load_memory()

    results = []

    for item in data:
        if query.lower() in item.get("issue", "").lower():
            results.append(item)

    return results[:3]