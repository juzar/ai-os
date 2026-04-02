import sys
from ai.executor import run_model

def main():
    if len(sys.argv) < 3:
        print("\nUsage: ai <mode> <query>\n")
        print("Modes: devops | research | general\n")
        return

    mode = sys.argv[1]
    query = " ".join(sys.argv[2:])

    print(f"\n⚡ Mode: {mode}")
    print(f"🧠 Query: {query}\n")

    result = run_model(mode, query)

    print("\n🔥 RESULT:\n")
    print(result)


if __name__ == "__main__":
    main()