import subprocess
def run(cmd): return subprocess.getoutput(cmd)
def analyze_pods(): return run("kubectl get pods -A")
def debug_pod(pod): return run(f"kubectl logs {pod}")
