import re

def extract_commands(text):
    patterns = [
        r"(kubectl[^\n]+)",
        r"(az[^\n]+)",
        r"(aws[^\n]+)"
    ]

    commands = []

    for pattern in patterns:
        commands += re.findall(pattern, text)

    return commands[:3]  # limit execution