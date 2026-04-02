
def detect_mode(text):
    text = text.lower()
    if "error" in text or "down" in text:
        return "incident"
    if "design" in text:
        return "architecture"
    return "devops"
