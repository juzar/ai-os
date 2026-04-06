import subprocess

ALLOWED = {
    "az account show": ["az", "account", "show"],
    "az account list": ["az", "account", "list"],
    "az vm list": ["az", "vm", "list"],
    "kubectl get pods": ["kubectl", "get", "pods"]
}


def run_command(cmd):

    if cmd not in ALLOWED:
        return "❌ Command not allowed"

    try:
        result = subprocess.run(
            ALLOWED[cmd],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            return f"[ERROR]\n{result.stderr}"

        return result.stdout

    except subprocess.TimeoutExpired:
        return "[ERROR] Command timed out"

    except Exception as e:
        return f"[ERROR] {e}"