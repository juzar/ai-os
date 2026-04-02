import subprocess

def run(cmd):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout or result.stderr


# ===== TOKEN-OPTIMIZED POD ANALYSIS =====
def analyze_pods():
    output = run("kubectl get pods -A")

    lines = output.split("\n")

    # 🔥 Only problematic pods
    filtered = [
        l for l in lines
        if "CrashLoopBackOff" in l or "Error" in l or "Pending" in l
    ]

    return "\n".join(filtered[:10])  # limit output


# ===== BASIC HELPERS =====
def describe_pod(pod, namespace="default"):
    return run(f"kubectl describe pod {pod} -n {namespace}")


def get_logs(pod, namespace="default"):
    return run(f"kubectl logs {pod} -n {namespace}")


# ===== TARGETED DEBUG (TOKEN OPTIMIZED) =====
def debug_pod(pod, namespace="default"):
    logs = get_logs(pod, namespace)

    # 🔥 Only last 50 lines (important)
    logs = "\n".join(logs.split("\n")[-50:])

    return f"""
==== RECENT POD LOGS ====
{logs}
"""