from langchain_core.messages import HumanMessage, SystemMessage
from src.app.llm import get_llm

def main():
    llm = get_llm()
    msgs = [
        SystemMessage(content="You are a helpful assistant. Answer in French."),
        HumanMessage(content="Explique en 3 phrases ce qu'est un agent IA.")
    ]
    resp = llm.invoke(msgs)
    print(resp.content)

if __name__ == "__main__":
    main()
