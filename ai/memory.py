import json
from pathlib import Path

FILE = Path("memory.json")


def load():
    if FILE.exists():
        return json.loads(FILE.read_text())
    return []


def save_memory(entry):
    data = load()

    # 🔥 Trim large inputs (token optimization)
    if len(entry["issue"]) > 300:
        entry["issue"] = entry["issue"][:300]

    entry["score"] = 1
    data.append(entry)

    FILE.write_text(json.dumps(data, indent=2))


def search_memory(query):
    memory = load()

    matches = [
        x for x in memory
        if query.lower() in x["issue"].lower()
    ]

    # 🔥 Rank by score
    matches.sort(key=lambda x: x.get("score", 0), reverse=True)

    return matches[:3]  # top results


def boost_memory(query):
    data = load()

    for item in data:
        if query.lower() in item["issue"].lower():
            item["score"] = item.get("score", 1) + 1

    FILE.write_text(json.dumps(data, indent=2))