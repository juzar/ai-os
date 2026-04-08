import json
from pathlib import Path
import time

DIR = Path("memory_store")
DIR.mkdir(exist_ok=True)

MAX_FILES = 100


def _file():
    return DIR / f"{int(time.time())}.json"


def _cleanup():
    files = sorted(DIR.glob("*.json"), key=lambda x: x.stat().st_mtime)

    if len(files) > MAX_FILES:
        for f in files[:-MAX_FILES]:
            try:
                f.unlink()
            except:
                pass


def save_memory(entry):
    try:
        f = _file()
        f.write_text(json.dumps(entry, indent=2))
        _cleanup()
    except:
        pass


def search_memory(query, limit=3):
    results = []

    for file in DIR.glob("*.json"):
        try:
            data = json.loads(file.read_text())

            score = 0
            issue = data.get("issue", "").lower()

            if query.lower() in issue:
                score += 2

            for w in query.split():
                if w.lower() in issue:
                    score += 1

            if score > 0:
                results.append({**data, "score": score})

        except:
            continue

    return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]