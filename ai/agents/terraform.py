import subprocess
from ai.intelligence.terraform_diff import analyze_diff

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


def analyze():
    plan = run("terraform plan -no-color")

    if "Error" in plan:
        return f"Terraform Error:\n{plan}"

    # 🔥 Intelligent diff
    return analyze_diff(plan)