import shutil
import subprocess
from ai.logger import log_error

_WINDOWS_AZ_PATH = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

COMMANDS = {
    "az account show":  ["account", "show"],
    "az group list":    ["group", "list"],
    "az vm list":       ["vm", "list"],
    "az resource list": ["resource", "list"],
}


def _az_path():
    found = shutil.which("az")
    if found:
        return found
    return _WINDOWS_AZ_PATH


def run_command(cmd):
    if cmd not in COMMANDS:
        return "❌ Command not allowed"

    az = _az_path()
    args = [az] + COMMANDS[cmd]

    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            return f"[AZ ERROR]\n{result.stderr}"

        return result.stdout

    except FileNotFoundError:
        return f"❌ Azure CLI not found (tried: {az})"

    except subprocess.TimeoutExpired:
        return "❌ Command timed out"

    except Exception as e:
        log_error("INFRA", str(e))
        return f"[ERROR] {e}"
