from ai.intelligence.terraform_diff import analyze_diff


def analyze_terraform(plan_output=""):
    if not plan_output:
        return "[Terraform] Pass plan output as argument: analyze_terraform(plan_output='...')"
    return analyze_diff(plan_output)


def plan_summary(plan_output=""):
    if not plan_output:
        return "[Terraform] Pass plan output as argument: plan_summary(plan_output='...')"
    result = analyze_diff(plan_output)
    # return just the summary block (first part before risk line)
    lines = result.strip().split("\n")
    summary_lines = [l for l in lines if not l.startswith("Risk Level:")]
    return "\n".join(summary_lines).strip()
