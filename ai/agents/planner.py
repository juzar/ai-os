def plan_task(user_input):
    steps = []

    if "pr" in user_input.lower():
        steps = [
            "extract_repo",
            "load_local",
            "load_remote",
            "diff",
            "analyze",
            "approval",
            "create_pr"
        ]
    else:
        steps = ["analyze"]

    return steps