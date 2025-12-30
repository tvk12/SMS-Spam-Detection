import sqlite3
import os
from datetime import datetime

DB_PATH = "spam_detection.db"

import secrets

def init_db():
    """Initialize the database with the prediction_logs and api_keys tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            prediction TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_feedback TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def create_api_key() -> str:
    """Generate and store a new API key."""
    new_key = f"sk_live_{secrets.token_urlsafe(16)}"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO api_keys (key) VALUES (?)",
        (new_key,)
    )
    conn.commit()
    conn.close()
    return new_key

def check_api_key_valid(key: str) -> bool:
    """Check if an API key exists and is active."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM api_keys WHERE key = ? AND is_active = 1",
        (key,)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def log_prediction(text: str, prediction: str) -> int:
    """Log a prediction and return the log ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prediction_logs (text, prediction, timestamp) VALUES (?, ?, ?)",
        (text, prediction, datetime.now())
    )
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def update_feedback(log_id: int, feedback: str):
    """Update the feedback for a specific log ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE prediction_logs SET user_feedback = ? WHERE id = ?",
        (feedback, log_id)
    )
    conn.commit()
    conn.close()

def get_stats():
    """Get statistics for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total requests
    cursor.execute("SELECT COUNT(*) FROM prediction_logs")
    total_requests = cursor.fetchone()[0]
    
    # Spam vs Ham
    cursor.execute("SELECT prediction, COUNT(*) FROM prediction_logs GROUP BY prediction")
    distribution = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Correctness (based on feedback)
    cursor.execute("SELECT user_feedback, COUNT(*) FROM prediction_logs WHERE user_feedback IS NOT NULL GROUP BY user_feedback")
    feedback_stats = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        "total_requests": total_requests,
        "distribution": distribution,
        "feedback_stats": feedback_stats
    }

def get_recent_logs(limit: int = 5):
    """Fetch recent prediction logs."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Allow accessing columns by name
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, text, prediction, timestamp, user_feedback FROM prediction_logs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_daily_stats(days: int = 7):
    """Fetch prediction counts grouped by date for the last N days."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(timestamp) as date, prediction, COUNT(*) as count 
        FROM prediction_logs 
        WHERE timestamp >= date('now', ?) 
        GROUP BY date, prediction 
        ORDER BY date ASC
    ''', (f'-{days} days',))
    rows = cursor.fetchall()
    conn.close()
    
    # Process into structured format
    stats = {} # { "YYYY-MM-DD": {"Spam": 0, "Ham": 0} }
    for date, pred, count in rows:
        if date not in stats: stats[date] = {"Spam": 0, "Ham": 0}
        stats[date][pred] = count
        
    return stats

def clear_all_logs():
    """Clear all prediction logs (Admin function)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prediction_logs")
    # Reset Sequence? Optional but good for demo
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='prediction_logs'")
    conn.commit()
    conn.close()

# Initialize DB on import (or you can call it explicitly in startup)
init_db()
