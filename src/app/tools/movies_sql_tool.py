from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

from src.app.llm import get_llm


ROOT = Path(__file__).resolve().parents[3]  # src/app/tools -> project root
DB_PATH = ROOT / "data" / "movies.db"

# On autorise uniquement des SELECT sur la table movies
SELECT_ONLY = re.compile(r"^\s*select\b", re.IGNORECASE)
FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|pragma|attach|detach|vacuum)\b", re.IGNORECASE)


def _rows_to_json(cursor: sqlite3.Cursor, rows: list[tuple[Any, ...]]) -> str:
    cols = [d[0] for d in cursor.description] if cursor.description else []
    data = [dict(zip(cols, r)) for r in rows]
    return json.dumps(data, ensure_ascii=False)


@tool
def query_movies_from_nl(question_fr: str) -> str:
    """
    À partir d'une question en français, génère une requête SQL SELECT sur la table movies,
    l'exécute sur data/movies.db, et renvoie les résultats en JSON.

    Table: movies(id, movie_name, rate, release_date)
    """
    if not DB_PATH.exists():
        return f"Erreur: base introuvable à {DB_PATH}. Lance d'abord: python scripts\\init_db.py"

    llm = get_llm()

    system = SystemMessage(content=(
        "Tu es un assistant qui écrit du SQL pour SQLite.\n"
        "Tu dois répondre UNIQUEMENT avec une requête SQL (pas de texte).\n"
        "Contraintes strictes:\n"
        "- Uniquement SELECT\n"
        "- Uniquement sur la table movies\n"
        "- Colonnes disponibles: id, movie_name, rate, release_date\n"
        "- Limite par défaut: LIMIT 20\n"
        "- Si l'utilisateur demande 'les meilleurs', trier par rate DESC puis release_date DESC\n"
        "- Si l'utilisateur parle d'une année, filtre sur release_date entre YYYY-01-01 et YYYY-12-31\n"
        "- Ne jamais utiliser INSERT/UPDATE/DELETE/DROP/ALTER/PRAGMA\n"
    ))

    prompt = HumanMessage(content=f"Question: {question_fr}\nSQL:")
    sql = llm.invoke([system, prompt]).content.strip()

    # Sécurité minimale: on bloque tout sauf SELECT + mots interdits
    if not SELECT_ONLY.match(sql):
        return "Erreur: SQL rejeté (doit commencer par SELECT)."
    if FORBIDDEN.search(sql):
        return "Erreur: SQL rejeté (contient une opération interdite)."
    if "movies" not in sql.lower():
        return "Erreur: SQL rejeté (doit interroger la table movies)."
    if "limit" not in sql.lower():
        sql = sql.rstrip(";") + " LIMIT 20;"

    # Exécution DB
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = None
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return _rows_to_json(cur, rows)
    except Exception as e:
        return f"Erreur exécution SQL: {e}\nSQL: {sql}"
    finally:
        try:
            conn.close()
        except Exception:
            pass
