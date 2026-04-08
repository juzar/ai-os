import sys
from ai.executor import run_model
from ai.chat import chat_loop


def main():

    # CLI MODE
    if len(sys.argv) > 2:
        mode = sys.argv[1]
        query = " ".join(sys.argv[2:])

        result = run_model(mode, query)
        print(result)
        return

    # CHAT MODE
    chat_loop()


if __name__ == "__main__":
    main()