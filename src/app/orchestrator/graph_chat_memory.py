from typing import TypedDict, Annotated, List

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import AnyMessage, SystemMessage

from src.app.llm import get_llm


# 1) L'état du graphe : une liste de messages.
# add_messages indique à LangGraph comment "concaténer" l'historique.
class ChatState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


def llm_node(state: ChatState) -> dict:
    """
    Node unique:
    - prend les messages existants (déjà mémorisés par LangGraph)
    - ajoute un SystemMessage (règles)
    - appelle le LLM
    - renvoie le nouveau message assistant
    """
    llm = get_llm()

    system = SystemMessage(content="Tu es un assistant utile. Réponds en français.")
    msgs = [system] + state["messages"]

    resp = llm.invoke(msgs)
    return {"messages": [resp]}


def build_graph():
    """
    On construit un StateGraph avec:
    - 1 node 'llm'
    - un checkpointer InMemorySaver pour mémoriser l'historique par thread_id
    """
    g = StateGraph(ChatState)
    g.add_node("llm", llm_node)
    g.set_entry_point("llm")

    # Le checkpointer stocke l'historique par thread_id
    checkpointer = InMemorySaver()
    return g.compile(checkpointer=checkpointer)


# On compile une fois et on réutilise le même graphe
GRAPH = build_graph()


def chat_once(user_text: str, thread_id: str) -> str:
    """
    Envoie 1 message utilisateur dans un thread.
    LangGraph récupère automatiquement l'historique du thread,
    ajoute le nouveau message, appelle llm_node, et sauvegarde.
    """
    config = {"configurable": {"thread_id": thread_id}}

    out_state = GRAPH.invoke(
        {"messages": [("human", user_text)]},
        config=config,
    )
    return out_state["messages"][-1].content
