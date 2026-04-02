import time
from dotenv import dotenv_values
from openai import OpenAI
import anthropic
import google.generativeai as genai

# ===== LOAD ENV =====
config = dotenv_values(".env")

ANTHROPIC_API_KEY = config.get("ANTHROPIC_API_KEY")
PERPLEXITY_API_KEY = config.get("PERPLEXITY_API_KEY")
GEMINI_API_KEY = config.get("GEMINI_API_KEY")

# ===== MODEL CONFIG =====
MODEL_CONFIG = {
    "claude": {
        "strong": "claude-3-5-sonnet-latest",
        "fast": "claude-haiku-4-5-20251001"
    },
    "perplexity": {
        "research": "llama-3.1-sonar-large-128k-online"
    },
    "gemini": {
        "pro": "gemini-1.5-pro-latest"
    }
}

# ===== ROUTING =====
def select_provider(mode):
    if mode == "devops":
        return ["claude", "perplexity", "gemini"]
    elif mode == "research":
        return ["perplexity", "claude", "gemini"]
    else:
        return ["claude", "gemini"]

# ===== CLAUDE =====
def call_claude(system_prompt, user_input):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=MODEL_CONFIG["claude"]["strong"],
        max_tokens=800,
        messages=[
            {"role": "user", "content": f"{system_prompt}\n\n{user_input}"}
        ]
    )

    return response.content[0].text

# ===== PERPLEXITY =====
def call_perplexity(system_prompt, user_input):
    client = OpenAI(
        api_key=PERPLEXITY_API_KEY,
        base_url="https://api.perplexity.ai"
    )

    response = client.chat.completions.create(
        model=MODEL_CONFIG["perplexity"]["research"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    return response.choices[0].message.content

# ===== GEMINI =====
def call_gemini(system_prompt, user_input):
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model=MODEL_CONFIG["gemini"]["pro"],
        contents=f"{system_prompt}\n\n{user_input}"
    )

    return response.text

# ===== RETRY SYSTEM =====
def retry(func, retries=2):
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"[Retry {i+1}] {e}")
            time.sleep(1)
    raise Exception("Retries exhausted")

# ===== EXECUTION ENGINE =====
def run_model(mode, user_input):
    system_prompt = """
You are a senior DevOps engineer.

Rules:
- Identify root cause
- Provide actionable fix
- Include CLI commands where possible
- Be precise, not verbose
"""

    providers = select_provider(mode)

    for provider in providers:
        try:
            print(f"[Using {provider.upper()}]")

            if provider == "claude":
                return retry(lambda: call_claude(system_prompt, user_input))

            elif provider == "perplexity":
                return retry(lambda: call_perplexity(system_prompt, user_input))

            elif provider == "gemini":
                return retry(lambda: call_gemini(system_prompt, user_input))

        except Exception as e:
            print(f"[{provider.upper()} FAILED] {e}")

    return "[ALL MODELS FAILED]"