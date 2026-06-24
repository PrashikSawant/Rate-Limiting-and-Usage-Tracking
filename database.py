"""
database.py
Sets up a tiny SQLite database to track API usage.
No server needed - it's just a file called usage.db
"""

import sqlite3
from datetime import datetime

DB_NAME = "usage.db"


def init_db():
    """Creates the usage_logs table if it doesn't already exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            estimated_cost REAL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def log_usage(username: str, endpoint: str, prompt_tokens: int,
              completion_tokens: int, total_tokens: int, estimated_cost: float):
    """Inserts one row into usage_logs every time a user makes a request."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usage_logs
        (username, endpoint, prompt_tokens, completion_tokens, total_tokens, estimated_cost, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        username, endpoint, prompt_tokens, completion_tokens,
        total_tokens, estimated_cost, datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def get_usage_for_user(username: str):
    """Returns all usage logs + totals for one user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT endpoint, prompt_tokens, completion_tokens, total_tokens, estimated_cost, timestamp
        FROM usage_logs
        WHERE username = ?
        ORDER BY timestamp DESC
    """, (username,))

    rows = cursor.fetchall()
    conn.close()

    logs = [
        {
            "endpoint": row[0],
            "prompt_tokens": row[1],
            "completion_tokens": row[2],
            "total_tokens": row[3],
            "estimated_cost": row[4],
            "timestamp": row[5],
        }
        for row in rows
    ]

    total_requests = len(logs)
    total_tokens_used = sum(log["total_tokens"] for log in logs)
    total_cost = sum(log["estimated_cost"] for log in logs)

    return {
        "username": username,
        "total_requests": total_requests,
        "total_tokens_used": total_tokens_used,
        "total_estimated_cost": round(total_cost, 6),
        "logs": logs,
    }