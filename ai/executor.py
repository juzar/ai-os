import time
import threading
from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import anthropic

# ===== LOAD ENV =====
config = dotenv_values(Path(__file__).resolve().parent.parent / ".env")

ANTHROPIC_API_KEY = config.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = config.get("OPENAI_API_KEY")

# ===== MODEL CONFIG =====
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
OPENAI_MODEL = "gpt-4o-mini"

# ===== PROMPT ENGINE =====
def get_prompt(mode):
    if mode == "devops":
        return """
You are a senior DevOps engineer.

- Identify root cause
- Provide actionable fix
- Include CLI commands (kubectl, az, aws)
- Keep it precise
"""
    elif mode == "research":
        return """
You are a technical researcher.

- Provide structured insights
- Compare approaches
- Focus on latest best practices
"""
    elif mode == "incident":
        return """
You are in INCIDENT RESPONSE MODE.

- Diagnose quickly
- List probable causes
- Suggest immediate mitigation
- Then long-term fix
"""
    else:
        return "You are a helpful assistant."

# ===== CLAUDE =====
def call_claude(system_prompt, user_input):
    if not ANTHROPIC_API_KEY:
        raise Exception("Missing ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": f"{system_prompt}\n\n{user_input}"
            }
        ]
    )

    return response.content[0].text

# ===== OPENAI =====
def call_openai(system_prompt, user_input):
    if not OPENAI_API_KEY:
        raise Exception("Missing OPENAI_API_KEY")

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    return response.choices[0].message.content

# ===== RETRY SYSTEM =====
def retry(func, retries=2):
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"[Retry {i+1}] {e}")
            time.sleep(1)
    return f"[FAILED AFTER RETRIES]"

# ===== EXECUTION ENGINE (PARALLEL) =====
def run_model(mode, user_input):
    system_prompt = get_prompt(mode)

    results = {}

    def run_claude():
        try:
            results["claude"] = retry(lambda: call_claude(system_prompt, user_input))
        except Exception as e:
            results["claude"] = f"[ERROR] {e}"

    def run_openai():
        try:
            results["openai"] = retry(lambda: call_openai(system_prompt, user_input))
        except Exception as e:
            results["openai"] = f"[ERROR] {e}"

    t1 = threading.Thread(target=run_claude)
    t2 = threading.Thread(target=run_openai)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # ===== OUTPUT FORMAT =====
    final_output = f"""
================ AI ANALYSIS ================

PRIMARY (CLAUDE):
{results.get("claude")}

--------------------------------------------

SECONDARY (CHATGPT):
{results.get("openai")}

============================================
"""

    return final_output