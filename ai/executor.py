import os
from dotenv import load_dotenv

from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- OpenAI ---
from openai import OpenAI

# --- Claude ---
import anthropic

# --- Gemini (kept optional, warning ignored for now) ---
import google.generativeai as genai


# =========================
# CLAUDE (PRIMARY)
# =========================
def call_claude(system_prompt, user_input):
    import anthropic
    import os

    try:
        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": f"{system_prompt}\n\n{user_input}"
                }
            ]
        )

        return response.content[0].text

    except Exception as e:
        return f"[CLAUDE ERROR] {str(e)}"


# =========================
# PERPLEXITY (RESEARCH + FALLBACK)
# =========================
def call_perplexity(system_prompt, user_input):
    try:
        client = OpenAI(
            api_key=os.getenv("PERPLEXITY_API_KEY"),
            base_url="https://api.perplexity.ai"
        )

        response = client.chat.completions.create(
            model="llama-3.1-sonar-small-128k-online",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"[PERPLEXITY ERROR] {str(e)}"


# =========================
# GPT (FINAL FALLBACK)
# =========================
def call_gpt(system_prompt, user_input):
    try:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"[GPT ERROR] {str(e)}"


# =========================
# GEMINI (OPTIONAL)
# =========================
def call_gemini(system_prompt, user_input):
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        model = genai.GenerativeModel(
            "gemini-pro",
            system_instruction=system_prompt
        )

        return model.generate_content(user_input).text

    except Exception as e:
        return f"[GEMINI ERROR] {str(e)}"


# =========================
# MASTER ROUTER
# =========================
def run_model(mode, user_input):
    system_prompt = f"You are an expert in {mode}. Provide actionable answers."

    # 🔥 ONLY CLAUDE (for now)
    result = call_claude(system_prompt, user_input)

    if not result.startswith("[CLAUDE ERROR]"):
        return result

    return result