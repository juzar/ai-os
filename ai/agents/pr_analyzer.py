def summarize_changes(changes):
    summary = []

    for c in changes:
        summary.append(f"{c['type']} → {c['path']}")

    return "\n".join(summary[:50])


def risk_score(changes):
    score = 0

    for c in changes:
        path = c["path"]

        if "executor" in path or "brain" in path:
            score += 3
        elif "infra" in path or "agents" in path:
            score += 2
        else:
            score += 1

    if score >= 15:
        return "HIGH"
    elif score >= 7:
        return "MEDIUM"
    return "LOW"