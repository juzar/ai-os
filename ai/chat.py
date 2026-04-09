from ai.executor import run_model
from ai.session import add_message, get_messages

def chat_loop():
    print("🔥 AI-OS Chat Mode (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        history = get_messages()
        add_message("user", user_input)

        response = run_model("devops", user_input, history=history)

        print(f"\nAI:\n{response}\n")

        add_message("assistant", response)
