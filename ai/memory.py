import json
from pathlib import Path

FILE = Path("memory.json")


def load():
    if not FILE.exists():
        return []
    try:
        return json.loads(FILE.read_text())
    except:
        return []


def save_memory(entry):
    """
    Save interaction into memory
    """
    try:
        data = load()
        data.append(entry)

        # 🔒 prevent unlimited growth (keep last 100 entries)
        data = data[-100:]

        FILE.write_text(json.dumps(data, indent=2))

    except Exception as e:
        print(f"[MEMORY SAVE ERROR] {e}")


def search_memory(query, limit=3):
    """
    Search memory with scoring
    """
    data = load()
    results = []

    for item in data:
        score = 0

        issue = item.get("issue", "").lower()

        if query.lower() in issue:
            score += 2

        for word in query.split():
            if word.lower() in issue:
                score += 1

        if score > 0:
            results.append({**item, "score": score})

    return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]