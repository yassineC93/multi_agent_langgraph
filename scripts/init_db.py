from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "movies.db"

DDL = """
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_name TEXT NOT NULL,
    rate INTEGER NOT NULL CHECK(rate BETWEEN 1 AND 5),
    release_date TEXT NOT NULL -- ISO: YYYY-MM-DD
);
"""

SEED = [
    ("The Matrix", 5, "1999-03-31"),
    ("Inception", 5, "2010-07-16"),
    ("Interstellar", 5, "2014-11-07"),
    ("The Godfather", 5, "1972-03-24"),
    ("Titanic", 4, "1997-12-19"),
    ("Avatar", 4, "2009-12-18"),
    ("Dune", 4, "2021-10-22"),
    ("The Room", 1, "2003-06-27"),
]

def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(DDL)

        # Seed uniquement si table vide
        cur.execute("SELECT COUNT(*) FROM movies;")
        (count,) = cur.fetchone()
        if count == 0:
            cur.executemany(
                "INSERT INTO movies(movie_name, rate, release_date) VALUES(?,?,?);",
                SEED,
            )
            conn.commit()

        print(f"OK - DB ready at: {DB_PATH}")
        cur.execute("SELECT id, movie_name, rate, release_date FROM movies ORDER BY release_date LIMIT 5;")
        for row in cur.fetchall():
            print(row)

    finally:
        conn.close()

if __name__ == "__main__":
    main()
