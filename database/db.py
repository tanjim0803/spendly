import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = "spendly.db"

def get_db():
    """
    Opens a connection to the SQLite database, configures it for
    dictionary-like access and enables foreign key enforcement.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Creates the users and expenses tables if they do not already exist.
    """
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()

def seed_db():
    """
    Populates the database with a demo user and sample expenses if empty.
    """
    with get_db() as conn:
        # Check if users already exist to prevent duplicate seeding
        user_exists = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
        if user_exists:
            return

        # 1. Insert Demo User
        demo_password = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", demo_password)
        )
        user_id = cursor.lastrowid

        # 2. Insert Sample Expenses
        # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
        expenses = [
            (user_id, 15.50, "Food", "2026-10-20", "Lunch at Cafe"),
            (user_id, 25.00, "Transport", "2026-10-21", "Monthly Bus Pass"),
            (user_id, 60.00, "Bills", "2026-10-22", "Electricity Bill"),
            (user_id, 12.00, "Health", "2026-10-23", "Pharmacy - Vitamins"),
            (user_id, 18.00, "Entertainment", "2026-10-24", "Cinema Ticket"),
            (user_id, 35.00, "Shopping", "2026-10-25", "New T-shirt"),
            (user_id, 20.00, "Other", "2026-10-26", "Birthday Gift"),
            (user_id, 40.00, "Food", "2026-10-27", "Dinner with Friends"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
