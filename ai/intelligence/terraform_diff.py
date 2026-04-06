def analyze_diff(plan_output):
    lines = plan_output.split("\n")

    adds = []
    deletes = []
    changes = []

    for l in lines:
        if l.strip().startswith("+"):
            adds.append(l)
        elif l.strip().startswith("-"):
            deletes.append(l)
        elif l.strip().startswith("~"):
            changes.append(l)

    summary = f"""
Terraform Diff Summary:

+ Additions: {len(adds)}
- Deletions: {len(deletes)}
~ Modifications: {len(changes)}
"""

    risk = "LOW"

    if deletes:
        risk = "HIGH"
    elif changes:
        risk = "MEDIUM"

    return summary + f"\nRisk Level: {risk}"