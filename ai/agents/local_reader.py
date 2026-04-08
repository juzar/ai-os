from pathlib import Path

IGNORE = ["venv", "__pycache__", ".git", ".idea"]


def read_local_project(root="."):
    """
    Returns summarized local project structure + sample content
    """

    files = []

    for path in Path(root).rglob("*"):

        if any(i in str(path) for i in IGNORE):
            continue

        if path.is_file():
            try:
                rel = str(path).replace("\\", "/")
                size = path.stat().st_size

                files.append(f"{rel} ({size} bytes)")

            except:
                continue

    if not files:
        return "[LOCAL ERROR] No files found"

    # show only first 100 files (token safe)
    summary = "\n".join(files[:100])

    return f"""
PROJECT FILES:
{summary}
"""