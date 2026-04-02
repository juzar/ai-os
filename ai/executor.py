import time
import threading
from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import anthropic

from ai.memory import search_memory, save_memory, boost_memory
from ai.agents.kubernetes import analyze_pods, debug_pod
from ai.remediation import run_fix
from ai.utils import extract_commands

# ===== LOAD ENV =====
config = dotenv_values(Path(__file__).resolve().parent.parent / ".env")

ANTHROPIC_API_KEY = config.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = config.get("OPENAI_API_KEY")

CLAUDE_MODEL = "claude-haiku-4-5-20251001"
OPENAI_MODEL = "gpt-4o-mini"

# ===== PROMPTS =====
def get_prompt(mode):
    if mode == "devops":
        return """
You are a senior DevOps engineer.

- Identify root cause
- Provide actionable fix
- Include CLI commands (kubectl, az, aws)
- Be precise
"""
    elif mode == "incident":
        return """
You are in INCIDENT RESPONSE MODE.

- Diagnose quickly
- Provide mitigation first
- Then root cause
"""
    elif mode == "infra":
        return """
You are a cloud engineer.

- Troubleshoot infra issues
- Focus on Azure/AWS
"""
    else:
        return "You are a helpful assistant."

# ===== MODEL CALLS =====
def call_claude(prompt, user_input):
    if not ANTHROPIC_API_KEY:
        raise Exception("Missing ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=600,  # 🔥 reduced tokens
        messages=[
            {"role": "user", "content": f"{prompt}\n\n{user_input}"}
        ]
    )

    return response.content[0].text


def call_openai(prompt, user_input):
    if not OPENAI_API_KEY:
        raise Exception("Missing OPENAI_API_KEY")

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=500  # 🔥 reduced tokens
    )

    return response.choices[0].message.content


# ===== RETRY =====
def retry(func, retries=2):
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"[Retry {i+1}] {e}")
            time.sleep(1)
    return "[FAILED AFTER RETRIES]"


# ===== ROUTING =====
def should_use_parallel(mode):
    return mode in ["incident", "infra"]


# ===== EXECUTION ENGINE =====
def run_model(mode, user_input):

    # ===== MEMORY CHECK =====
    past = search_memory(user_input)
    if past:
        return f"⚠️ Found similar past issue:\n{past}"

    prompt = get_prompt(mode)

    # ===== SMART K8S CONTEXT =====
    if "pod" in user_input.lower() and "debug" not in user_input.lower():
        user_input += f"\n\nFailing Pods:\n{analyze_pods()}"

    # ===== TARGETED POD DEBUG =====
    if "debug pod" in user_input.lower():
        try:
            pod = user_input.split()[-1]
            user_input += f"\n\n{debug_pod(pod)}"
        except Exception:
            pass

    results = {}

    # ===== EXECUTION STRATEGY =====
    if should_use_parallel(mode):

        def run_claude():
            results["claude"] = retry(lambda: call_claude(prompt, user_input))

        def run_openai():
            results["openai"] = retry(lambda: call_openai(prompt, user_input))

        t1 = threading.Thread(target=run_claude)
        t2 = threading.Thread(target=run_openai)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

    else:
        results["claude"] = retry(lambda: call_claude(prompt, user_input))
        results["openai"] = "[SKIPPED FOR TOKEN EFFICIENCY]"

    claude_output = results.get("claude", "")
    openai_output = results.get("openai", "")

    # ===== SMART COMMAND EXTRACTION =====
    commands = extract_commands(claude_output)

    for cmd in commands:
        try:
            result = run_fix(cmd)
            print(f"\n⚡ {cmd}\n{result}")
        except Exception as e:
            print(f"[Remediation Error] {e}")

    # ===== MEMORY SAVE + BOOST =====
    save_memory({
        "issue": user_input[:300],
        "solution": claude_output
    })
    boost_memory(user_input)

    # ===== FINAL OUTPUT =====
    return f"""
================ AI ANALYSIS ================

PRIMARY (CLAUDE):
{claude_output}

--------------------------------------------

SECONDARY (CHATGPT):
{openai_output}

============================================
"""