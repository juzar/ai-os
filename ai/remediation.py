import subprocess


# 🚨 BLOCKED COMMANDS (NEVER RUN)
BLOCKED = [
    "rm -rf /",
    "shutdown",
    "reboot",
    "mkfs",
    "dd ",
    ":(){ :|:& };:"  # fork bomb
]


def is_safe(command):
    return not any(b in command for b in BLOCKED)


def run_fix(command):

    if not is_safe(command):
        return "❌ Command blocked (unsafe)"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        return result.stdout or result.stderr

    except Exception as e:
        return f"[ERROR] {e}"