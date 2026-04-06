from pathlib import Path

IGNORE_DIRS = ["venv", "__pycache__", ".git"]
MAX_FILES = 15
MAX_TOTAL_CHARS = 8000


def read_local_project(root="."):
    root_path = Path(root)

    collected = []
    total_chars = 0

    for file in root_path.rglob("*.py"):

        if any(ignored in str(file) for ignored in IGNORE_DIRS):
            continue

        try:
            content = file.read_text(encoding="utf-8")

            snippet = f"\nFILE: {file}\n{content}\n"

            if total_chars + len(snippet) > MAX_TOTAL_CHARS:
                break

            collected.append(snippet)
            total_chars += len(snippet)

            if len(collected) >= MAX_FILES:
                break

        except:
            continue

    return "".join(collected)