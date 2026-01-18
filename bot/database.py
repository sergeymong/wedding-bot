"""Простая база данных для хранения пользователей и связей сообщений"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List

DB_PATH = os.getenv("DB_PATH", "data/bot.db")


def init_db():
    """Инициализация базы данных"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей (гостей)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица связей: сообщение в группе → user_id гостя
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_links (
            admin_message_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def save_user(user_id: int, username: Optional[str], full_name: str):
    """Сохранить или обновить пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users (user_id, username, full_name, last_seen)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            full_name = excluded.full_name,
            last_seen = excluded.last_seen
    """, (user_id, username, full_name, datetime.now()))
    
    conn.commit()
    conn.close()


def get_all_users() -> List[int]:
    """Получить всех пользователей для рассылки"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return users


def get_users_count() -> int:
    """Количество пользователей"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    conn.close()
    return count


def save_message_link(admin_message_id: int, user_id: int):
    """Сохранить связь сообщения в группе с user_id"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO message_links (admin_message_id, user_id)
        VALUES (?, ?)
    """, (admin_message_id, user_id))
    
    conn.commit()
    conn.close()


def get_user_by_message(admin_message_id: int) -> Optional[int]:
    """Получить user_id по message_id в группе админов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id FROM message_links WHERE admin_message_id = ?
    """, (admin_message_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return row[0] if row else None
