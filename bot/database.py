"""База данных для хранения гостей и связей сообщений"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Tuple

DB_PATH = os.getenv("DB_PATH", "data/bot.db")


def init_db():
    """Инициализация базы данных"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица гостей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            first_visit INTEGER DEFAULT 1,
            rsvp_status TEXT,
            plus_one INTEGER DEFAULT 0,
            allergies TEXT,
            alcohol_pref TEXT,
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


def get_user(user_id: int) -> Optional[Tuple]:
    """Получить информацию о пользователе"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def is_first_visit(user_id: int) -> bool:
    """Проверить, первый ли это визит"""
    user = get_user(user_id)
    return user is None


def save_user(user_id: int, username: Optional[str], full_name: str, first_visit: bool = False):
    """Сохранить или обновить пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users (user_id, username, full_name, first_visit, last_seen)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            full_name = excluded.full_name,
            first_visit = 0,
            last_seen = excluded.last_seen
    """, (user_id, username, full_name, 1 if first_visit else 0, datetime.now()))
    
    conn.commit()
    conn.close()


def save_rsvp(user_id: int, status: str, plus_one: bool = False, allergies: str = None, alcohol: str = None):
    """Сохранить ответ гостя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE users SET 
            rsvp_status = ?,
            plus_one = ?,
            allergies = ?,
            alcohol_pref = ?
        WHERE user_id = ?
    """, (status, 1 if plus_one else 0, allergies, alcohol, user_id))
    
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


def get_confirmed_users() -> List[int]:
    """Получить подтвердивших участие"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE rsvp_status = 'confirmed'")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users


def get_stats() -> dict:
    """Статистика по гостям"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE rsvp_status = 'confirmed'")
    confirmed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE rsvp_status = 'declined'")
    declined = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE rsvp_status = 'confirmed' AND plus_one = 1")
    plus_ones = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE rsvp_status IS NULL")
    pending = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total': total,
        'confirmed': confirmed,
        'declined': declined,
        'plus_ones': plus_ones,
        'pending': pending,
        'total_guests': confirmed + plus_ones
    }


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
    cursor.execute("SELECT user_id FROM message_links WHERE admin_message_id = ?", (admin_message_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
