import sqlite3
from datetime import datetime

DB = "learning.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            topic     TEXT NOT NULL,
            created   TEXT
        )
    """)

    # Quiz sessions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            topic       TEXT,
            score       REAL,
            difficulty  REAL,
            timestamp   TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Weak topics table
    c.execute("""
        CREATE TABLE IF NOT EXISTS weak_topics (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER,
            topic    TEXT,
            score    REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Study plans table
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER,
            plan      TEXT,
            created   TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database ready!")


def create_user(name: str, topic: str) -> int:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (name, topic, created) VALUES (?,?,?)",
        (name, topic, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_user(name: str) -> dict:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE name=? ORDER BY id DESC LIMIT 1", (name,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "topic": row[2], "created": row[3]}
    return None


def save_session(user_id: int, topic: str, score: float, difficulty: float):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO sessions (user_id, topic, score, difficulty, timestamp) VALUES (?,?,?,?,?)",
        (user_id, topic, score, difficulty, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def save_weak_topics(user_id: int, topics: list):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM weak_topics WHERE user_id=?", (user_id,))
    for t in topics:
        c.execute(
            "INSERT INTO weak_topics (user_id, topic, score) VALUES (?,?,?)",
            (user_id, t["topic"], t["score"])
        )
    conn.commit()
    conn.close()


def save_study_plan(user_id: int, plan: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO study_plans (user_id, plan, created) VALUES (?,?,?)",
        (user_id, plan, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_sessions(user_id: int) -> list:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "SELECT topic, score, difficulty, timestamp FROM sessions WHERE user_id=? ORDER BY id DESC LIMIT 30",
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_weak_topics(user_id: int) -> list:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT topic, score FROM weak_topics WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_stats(user_id: int) -> dict:
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), AVG(score) FROM sessions WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return {
        "total_sessions": row[0] or 0,
        "avg_score": round(row[1] or 0, 1)
    }


if __name__ == "__main__":
    init_db()
    uid = create_user("Madhu", "Machine Learning")
    print(f"✅ User created: ID={uid}")
    save_session(uid, "Neural Networks", 75.0, 0.6)
    print("✅ Session saved!")
    print("Stats:", get_stats(uid))
