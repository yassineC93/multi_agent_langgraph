from typing import TypedDict, Annotated, List

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.messages import AnyMessage, SystemMessage

from src.app.llm import get_llm
from src.app.tools.datetime_tool import current_datetime


class ChatState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


TOOLS = [current_datetime]


def orchestrator_node(state: ChatState) -> dict:
    """
    Nœud LLM (orchestrateur):
    - voit l'historique
    - décide s'il doit appeler current_datetime
    - sinon répond directement
    """
    llm = get_llm().bind_tools(TOOLS)

    system = SystemMessage(content=(
        "Tu es un assistant orchestrateur. Réponds en français.\n"
        "Si l'utilisateur demande l'heure ou la date actuelle, "
        "utilise l'outil current_datetime.\n"
        "Après l'appel à l'outil, donne une réponse finale claire."
    ))

    msgs = [system] + state["messages"]
    resp = llm.invoke(msgs)

    return {"messages": [resp]}


def build_graph():
    g = StateGraph(ChatState)

    # 1) Orchestrateur (LLM)
    g.add_node("orchestrator", orchestrator_node)

    # 2) ToolNode : exécute current_datetime si demandé
    g.add_node("tools", ToolNode(TOOLS))

    # 3) Routing conditionnel
    g.add_conditional_edges("orchestrator", tools_condition)

    # 4) Après tool → retour au LLM
    g.add_edge("tools", "orchestrator")

    g.set_entry_point("orchestrator")

    checkpointer = InMemorySaver()
    return g.compile(checkpointer=checkpointer)


GRAPH = build_graph()


def chat_once(user_text: str, thread_id: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}

    out_state = GRAPH.invoke(
        {"messages": [("human", user_text)]},
        config=config,
    )

    return out_state["messages"][-1].content
