import json
import time
from pathlib import Path

SESSION_FILE = Path("sessions/active.json")
MAX_MESSAGES = 50


def load_session():
    if not SESSION_FILE.exists():
        return {"messages": []}

    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)

            # FIX 1: if list → wrap
            if isinstance(data, list):
                return {"messages": data}

            # FIX 2: missing key
            if "messages" not in data:
                data["messages"] = []

            # FIX 3: wrong type
            if not isinstance(data["messages"], list):
                data["messages"] = []

            return data

    except:
        return {"messages": []}


def save_session(data):

    messages = data.get("messages", [])

    # 🔥 CRITICAL FIX: enforce list
    if not isinstance(messages, list):
        messages = []

    # 🔥 CRITICAL FIX: safe slicing (NOT indexing)
    messages = messages[-MAX_MESSAGES:] if messages else []

    data["messages"] = messages

    SESSION_FILE.parent.mkdir(exist_ok=True)

    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_message(role, content):
    data = load_session()

    if not isinstance(data.get("messages"), list):
        data["messages"] = []

    data["messages"].append({
        "role": role,
        "content": content,
        "ts": time.time()
    })

    save_session(data)


def get_messages():
    data = load_session()

    if not isinstance(data.get("messages"), list):
        return []

    return data["messages"]