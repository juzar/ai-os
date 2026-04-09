import os
from pathlib import Path

IGNORE = ["venv", "__pycache__", ".git", ".idea"]


def get_local_file_map(root="."):
    """
    Read all local files into a dictionary
    { filepath: content }
    """
    file_map = {}

    for path in Path(root).rglob("*"):

        if any(ignore in str(path) for ignore in IGNORE):
            continue

        if path.is_file():
            try:
                rel_path = str(path).replace("\\", "/")
                content = path.read_text(encoding="utf-8")

                file_map[rel_path] = content

            except Exception:
                # skip unreadable files
                continue

    return file_map


def compare_maps(local_map, repo_map):
    """
    Compare local vs repo and return changes
    """
    changes = []

    for path, content in local_map.items():

        if path not in repo_map:
            changes.append({
                "type": "NEW",
                "path": path,
                "content": content
            })

        elif repo_map[path] != content:
            changes.append({
                "type": "MODIFIED",
                "path": path,
                "content": content
            })

    return changes