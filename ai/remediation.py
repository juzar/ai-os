import subprocess

# ===== SAFETY RULES =====
BLOCKED_KEYWORDS = [
    "delete",
    "rm -rf",
    "drop",
    "format",
    "shutdown",
    "reboot"
]


def is_safe(cmd):
    return not any(word in cmd.lower() for word in BLOCKED_KEYWORDS)


def confirm_execution(cmd):
    print(f"\n⚠️ Suggested Fix:\n{cmd}")
    choice = input("\nExecute this command? (y/n): ").strip().lower()
    return choice == "y"


def run_fix(cmd):
    if not is_safe(cmd):
        return f"❌ Blocked unsafe command: {cmd}"

    if not confirm_execution(cmd):
        return "❌ Skipped by user"

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    return result.stdout or result.stderr