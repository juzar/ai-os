import subprocess
from ai.logger import log_error

# ✅ Correct path (your system)
AZ_PATH = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"


def run_command(cmd):

    COMMANDS = {
        "az account show": [AZ_PATH, "account", "show"],
    }

    if cmd not in COMMANDS:
        return "❌ Command not allowed"

    try:
        result = subprocess.run(
            COMMANDS[cmd],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            return f"[AZ ERROR]\n{result.stderr}"

        return result.stdout

    except FileNotFoundError:
        return f"❌ Azure CLI not found at: {AZ_PATH}"

    except subprocess.TimeoutExpired:
        return "❌ Command timed out"

    except Exception as e:
        log_error("INFRA", str(e))
        return f"[ERROR] {e}"