from langchain_core.messages import SystemMessage, HumanMessage
from src.app.llm import get_llm

def main() -> None:
    llm = get_llm()

    # Historique de conversation en mémoire (dans Python)
    history = [
        SystemMessage(content="Tu es un assistant utile. Réponds en français.")
    ]

    print("CLI Chat (tape 'exit' pour quitter)\n")

    while True:
        user_text = input("toi> ").strip()
        if user_text.lower() in {"exit", "quit"}:
            print("bye!")
            break
        if not user_text:
            continue

        # 1) On ajoute le message utilisateur à l'historique
        history.append(HumanMessage(content=user_text))

        # 2) On envoie TOUT l'historique au modèle
        #    (c'est ça la mémoire multi-tour)
        resp = llm.invoke(history)

        # 3) On ajoute la réponse à l'historique
        history.append(resp)

        print(f"ia> {resp.content}\n")

if __name__ == "__main__":
    main()
