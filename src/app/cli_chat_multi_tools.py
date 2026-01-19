from src.app.orchestrator.graph_chat_multi_tools import chat_once


def main() -> None:
    print("CLI Chat LangGraph + Multi Tools (exit pour quitter)")
    thread_id = input("thread_id > ").strip() or "default"
    print(f"\nSession démarrée avec thread_id = {thread_id}\n")

    while True:
        user_text = input("toi> ").strip()
        if user_text.lower() in {"exit", "quit"}:
            print("bye!")
            break
        if not user_text:
            continue

        answer = chat_once(user_text=user_text, thread_id=thread_id)
        print(f"ia> {answer}\n")


if __name__ == "__main__":
    main()
