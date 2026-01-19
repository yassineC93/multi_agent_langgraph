from langchain_core.tools import tool


@tool
def calc(expression: str) -> str:
    """
    Calcule une expression mathématique simple.
    Autorisés: chiffres, + - * / ( ) .
    """
    print('utilisation du tool calc')
    allowed = set("0123456789+-*/(). ")
    if any(c not in allowed for c in expression):
        return "Erreur: caractères non autorisés."

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Erreur de calcul: {e}"
