import json
from pathlib import Path

FILE = Path("session.json")


def load():
    if not FILE.exists():
        return {"messages": []}
    try:
        return json.loads(FILE.read_text())
    except:
        return {"messages": []}


def save(data):
    FILE.write_text(json.dumps(data, indent=2))


def add_message(role, content):
    data = load()
    data["messages"].append({"role": role, "content": content})
    save(data)


def get_messages():
    return load()["messages"]