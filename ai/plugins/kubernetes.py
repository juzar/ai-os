
import subprocess
from ai.executor import run_model

def analyze_kube(namespace):
    pods = subprocess.getoutput(f"kubectl get pods -n {namespace}")
    return run_model("kubernetes", pods)
