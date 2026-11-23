# db.py — простой вариант на sqlite3, без SQLAlchemy и async

import sqlite3
from contextlib import closing
from typing import List, Optional, Dict, Any

# путь к файлу базы
DB_PATH = "data.db"


def init_db():
    """
    Создаём файл data.db и таблицы, если их ещё нет.
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        # Таблица товаров
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                price REAL NOT NULL,
                old_price REAL,
                photo_id TEXT
            )
        """)
        # Таблица пользователей бота (для рассылок)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE NOT NULL
            )
        """)
        conn.commit()


def add_product(title: str, description: str, price: float, photo_id: Optional[str]) -> int:
    """
    Добавляет товар в таблицу products.
    Возвращает id добавленного товара.
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products (title, description, price, old_price, photo_id) "
            "VALUES (?, ?, ?, NULL, ?)",
            (title, description, price, photo_id),
        )
        conn.commit()
        return cur.lastrowid


def list_products() -> List[Dict[str, Any]]:
    """
    Возвращает список всех товаров в виде списка словарей.
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title, description, price, old_price, photo_id FROM products ORDER BY id")
        rows = cur.fetchall()
        products: List[Dict[str, Any]] = []
        for r in rows:
            products.append({
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "price": r[3],
                "old_price": r[4],
                "photo_id": r[5],
            })
        return products


def set_price(product_id: int, new_price: float) -> Optional[Dict[str, Any]]:
    """
    Меняет цену товара. Если новая цена ниже старой — запоминаем старую в old_price,
    чтобы показывать зачёркнутой.
    Возвращает словарь с обновлённым товаром или None, если не найден.
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, description, price, old_price, photo_id "
            "FROM products WHERE id = ?",
            (product_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        old_price = row[3]
        if new_price < old_price:
            new_old_price = old_price
        else:
            new_old_price = None

        cur.execute(
            "UPDATE products SET price = ?, old_price = ? WHERE id = ?",
            (new_price, new_old_price, product_id),
        )
        conn.commit()

        return {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "price": new_price,
            "old_price": new_old_price,
            "photo_id": row[5],
        }


def add_user_if_not_exists(tg_id: int):
    """
    Добавляет пользователя в таблицу users, если его там ещё нет.
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id,))
        row = cur.fetchone()
        if row:
            return
        cur.execute("INSERT INTO users (tg_id) VALUES (?)", (tg_id,))
        conn.commit()


def list_users() -> List[int]:
    """
    Возвращает список Telegram ID всех пользователей бота.
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT tg_id FROM users")
        rows = cur.fetchall()
        return [r[0] for r in rows]


if __name__ == "__main__":
    # если запустить python db.py — просто создаст базу и таблицы
    init_db()
    print("База данных инициализирована.")
