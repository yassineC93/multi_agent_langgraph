from langchain_ollama import ChatOllama

def get_llm():
    return ChatOllama(
        model="phi3:mini",
        temperature=0,
        base_url="http://localhost:11434",
    )
