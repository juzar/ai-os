def score_pr(changes_text):
    risk = "LOW"
    reasons = []

    text = changes_text.lower()

    if any(x in text for x in ["security", "auth", "iam", "policy"]):
        risk = "HIGH"
        reasons.append("Security-related changes")

    if any(x in text for x in ["terraform", "infrastructure", "vpc", "subnet"]):
        risk = "HIGH"
        reasons.append("Infrastructure modification")

    if any(x in text for x in ["delete", "remove", "destroy"]):
        risk = "HIGH"
        reasons.append("Destructive change detected")

    if "refactor" in text or "rename" in text:
        risk = "MEDIUM"
        reasons.append("Code restructuring")

    if not reasons:
        reasons.append("No risky patterns detected")

    return {
        "risk": risk,
        "reasons": reasons
    }