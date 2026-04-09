import subprocess


def _run_kubectl(args, timeout=15):
    try:
        result = subprocess.run(
            ["kubectl"] + args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode != 0:
            return f"[kubectl error]\n{result.stderr.strip()}"
        return result.stdout.strip()
    except FileNotFoundError:
        return "❌ kubectl not found — is it installed and on PATH?"
    except subprocess.TimeoutExpired:
        return "❌ kubectl timed out"
    except Exception as e:
        return f"[ERROR] {e}"


def analyze_pods():
    return _run_kubectl(["get", "pods", "--all-namespaces", "-o", "wide"])


def debug_pod():
    return _run_kubectl(["get", "events", "--all-namespaces", "--sort-by=.lastTimestamp"])
