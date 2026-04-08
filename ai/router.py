def detect_mode(user_input):

    text = user_input.lower()

    if "github" in text or "pr" in text or "pull request" in text:
        return "github"

    if "terraform" in text or "plan" in text:
        return "terraform"

    if "infra" in text or "vm" in text:
        return "infra"

    if "pod" in text or "k8s" in text:
        return "devops"

    return "devops"