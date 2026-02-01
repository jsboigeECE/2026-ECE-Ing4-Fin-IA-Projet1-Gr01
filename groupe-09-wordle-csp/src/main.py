import sys

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except Exception:
    KEYBOARD_AVAILABLE = False

from llm_agent import interroger_agent_wordle, load_dictionary


def main():
    print("--- Wordle Solver (Ollama + CSP) ---")
    print("Input format: GUESS FEEDBACK  (V=green, J=yellow, G=gray)")
    print("Examples: ORATE GVVJG   |   ORATE -> GVVJG")
    print("Quit: press ESC and Enter.\n")

    dictionary = load_dictionary("wordle.txt")
    if not dictionary:
        print("Dictionary is empty. Please check 'wordle.txt'.")
        sys.exit(1)

    attempts = []  # persistent history during the session

    while True:
        user_text = input("Enter your attempt: ").strip()

        if KEYBOARD_AVAILABLE and keyboard.is_pressed("esc"):
            print("Shutting down... Goodbye!")
            sys.exit(0)

        if not user_text:
            continue

        print("\nThinking...\n")

        try:
            result = interroger_agent_wordle(user_text, dictionary, attempts)
            print(result)
        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()

