from typing import TypedDict, Annotated, List

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.messages import AnyMessage, SystemMessage

from src.app.llm import get_llm
from src.app.tools.datetime_tool import current_datetime
from src.app.tools.calc import calc
from src.app.tools.movies_sql_tool import query_movies_from_nl


class ChatState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


TOOLS = [current_datetime, calc, query_movies_from_nl]


def orchestrator_node(state: ChatState) -> dict:
    """
    Orchestrateur LLM :
    - voit l’historique
    - décide s’il faut appeler datetime ou calc
    - ou répond directement
    """
    llm = get_llm().bind_tools(TOOLS)

    system = SystemMessage(
    content=(
        "Tu es un assistant orchestrateur. Réponds en français.\n"
        "Tu as accès à des outils, mais tu ne dois les utiliser QUE si nécessaire.\n"
        "Outils:\n"
        "- current_datetime : date/heure actuelles\n"
        "- calc : calcul mathématique\n"
        "- query_movies_from_nl : interroger la base SQLite movies (notes, dates de sortie)\n"
        "Règles:\n"
        "1) Si la demande est un salut, une question générale, ou ne nécessite pas de donnée externe/calcul, "
        "réponds directement en texte (sans appeler d'outil).\n"
        "2) Utilise current_datetime uniquement pour donner la date/heure actuelles.\n"
        "3) Utilise calc uniquement pour calculer une expression mathématique.\n"
        "4) Après un appel d’outil, tu dois produire une réponse finale en texte clair.\n"
        "5) Utilise query_movies_from_nl si la question porte sur des films, notes, meilleurs films, films par année, etc.\n"
        "6) Après un appel d’outil, résume les résultats de façon lisible (pas juste du JSON brut).\n"
        "IMPORTANT: Ne renvoie jamais de JSON, jamais de 'name/parameters'. Réponds toujours en texte naturel."
        )
    )

    msgs = [system] + state["messages"]
    resp = llm.invoke(msgs)

    return {"messages": [resp]}


def build_graph():
    g = StateGraph(ChatState)

    # Nœud principal (cerveau)
    g.add_node("orchestrator", orchestrator_node)

    # Nœud outils (exécuteur)
    g.add_node("tools", ToolNode(TOOLS))

    # Si le LLM appelle un tool → tools, sinon → fin
    g.add_conditional_edges("orchestrator", tools_condition)

    # Après un tool → retour à l’orchestrateur
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
