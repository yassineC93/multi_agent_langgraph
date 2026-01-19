from datetime import datetime
from langchain_core.tools import tool


@tool
def current_datetime() -> str:
    """
    Retourne la date et l'heure actuelles (heure locale).
    """
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")
