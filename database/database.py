import sqlite3
import os
from datetime import datetime

_data_dir = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(_data_dir, "bot_data.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            registered_at TEXT,
            current_day INTEGER DEFAULT 0,
            plan_started_at TEXT,
            morning_time TEXT DEFAULT '08:00',
            evening_time TEXT DEFAULT '21:00',
            notifications_enabled INTEGER DEFAULT 1,
            timezone TEXT DEFAULT 'Europe/Moscow'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS process_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            created_at TEXT,
            situation TEXT,
            discomfort_before INTEGER,
            state_after TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS gratitude_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            created_at TEXT,
            text TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS mini_process_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            created_at TEXT,
            trigger_text TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            created_at TEXT,
            phase1_phrase TEXT,
            phase2_phrase TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS weekly_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week_number INTEGER,
            created_at TEXT,
            changes TEXT,
            patterns TEXT,
            insights TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS day_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            day_number INTEGER,
            completed_at TEXT,
            evening_answer TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def create_user(user_id: int, username: str, full_name: str):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id, username, full_name, registered_at) VALUES (?, ?, ?, ?)",
        (user_id, username, full_name, now)
    )
    conn.commit()
    conn.close()


def start_plan(user_id: int):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "UPDATE users SET current_day = 1, plan_started_at = ? WHERE user_id = ?",
        (now, user_id)
    )
    conn.commit()
    conn.close()


def advance_day(user_id: int):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET current_day = current_day + 1 WHERE user_id = ? AND current_day <= 30",
        (user_id,)
    )
    conn.commit()
    conn.close()


def complete_day(user_id: int, day_number: int, evening_answer: str = ""):
    conn = get_conn()
    now = datetime.now().isoformat()
    existing = conn.execute(
        "SELECT id FROM day_completions WHERE user_id = ? AND day_number = ?",
        (user_id, day_number)
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO day_completions (user_id, day_number, completed_at, evening_answer) VALUES (?, ?, ?, ?)",
            (user_id, day_number, now, evening_answer)
        )
        advance_day(user_id)
    conn.commit()
    conn.close()


def is_day_completed(user_id: int, day_number: int) -> bool:
    conn = get_conn()
    result = conn.execute(
        "SELECT id FROM day_completions WHERE user_id = ? AND day_number = ?",
        (user_id, day_number)
    ).fetchone()
    conn.close()
    return result is not None


def save_process_entry(user_id: int, situation: str, discomfort_before: int, state_after: str, notes: str = ""):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO process_entries (user_id, created_at, situation, discomfort_before, state_after, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, now, situation, discomfort_before, state_after, notes)
    )
    conn.commit()
    conn.close()


def save_gratitude(user_id: int, text: str):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO gratitude_entries (user_id, created_at, text) VALUES (?, ?, ?)",
        (user_id, now, text)
    )
    conn.commit()
    conn.close()


def save_mini_process(user_id: int, trigger_text: str = ""):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO mini_process_log (user_id, created_at, trigger_text) VALUES (?, ?, ?)",
        (user_id, now, trigger_text)
    )
    conn.commit()
    conn.close()


def save_vocabulary(user_id: int, phase1: str, phase2: str):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO vocabulary_log (user_id, created_at, phase1_phrase, phase2_phrase) VALUES (?, ?, ?, ?)",
        (user_id, now, phase1, phase2)
    )
    conn.commit()
    conn.close()


def save_weekly_review(user_id: int, week_number: int, changes: str, patterns: str, insights: str):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO weekly_reviews (user_id, week_number, created_at, changes, patterns, insights) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, week_number, now, changes, patterns, insights)
    )
    conn.commit()
    conn.close()


def update_settings(user_id: int, morning_time: str = None, evening_time: str = None,
                    notifications_enabled: int = None, timezone: str = None):
    conn = get_conn()
    if morning_time:
        conn.execute("UPDATE users SET morning_time = ? WHERE user_id = ?", (morning_time, user_id))
    if evening_time:
        conn.execute("UPDATE users SET evening_time = ? WHERE user_id = ?", (evening_time, user_id))
    if notifications_enabled is not None:
        conn.execute("UPDATE users SET notifications_enabled = ? WHERE user_id = ?", (notifications_enabled, user_id))
    if timezone:
        conn.execute("UPDATE users SET timezone = ? WHERE user_id = ?", (timezone, user_id))
    conn.commit()
    conn.close()


def get_stats(user_id: int) -> dict:
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return {}

    process_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM process_entries WHERE user_id = ?", (user_id,)
    ).fetchone()["cnt"]

    mini_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM mini_process_log WHERE user_id = ?", (user_id,)
    ).fetchone()["cnt"]

    gratitude_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM gratitude_entries WHERE user_id = ?", (user_id,)
    ).fetchone()["cnt"]

    days_completed = conn.execute(
        "SELECT COUNT(*) as cnt FROM day_completions WHERE user_id = ?", (user_id,)
    ).fetchone()["cnt"]

    conn.close()
    return {
        "current_day": user["current_day"],
        "process_count": process_count,
        "mini_count": mini_count,
        "gratitude_count": gratitude_count,
        "days_completed": days_completed,
        "plan_started_at": user["plan_started_at"],
    }


def get_all_users():
    conn = get_conn()
    users = conn.execute("SELECT * FROM users WHERE notifications_enabled = 1").fetchall()
    conn.close()
    return users


def get_recent_process_entries(user_id: int, limit: int = 5):
    conn = get_conn()
    entries = conn.execute(
        "SELECT * FROM process_entries WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return entries


def get_recent_gratitude(user_id: int, limit: int = 5):
    conn = get_conn()
    entries = conn.execute(
        "SELECT * FROM gratitude_entries WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return entries
