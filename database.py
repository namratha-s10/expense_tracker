import sqlite3
import datetime

DB_NAME = "expenses.db"

def init_db():
    """Initialize the database and create the expenses table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_expense(date, amount, category, note):
    """Add a new expense record."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (date, amount, category, note)
        VALUES (?, ?, ?, ?)
    ''', (date, amount, category, note))
    conn.commit()
    conn.close()

def delete_expense(expense_id):
    """Delete an expense by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()

def update_expense(expense_id, date, amount, category, note):
    """Update an existing expense."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE expenses 
        SET date = ?, amount = ?, category = ?, note = ?
        WHERE id = ?
    ''', (date, amount, category, note, expense_id))
    conn.commit()
    conn.close()

def fetch_expenses_by_month(month, year):
    """Fetch expenses for a specific month and year."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Format: YYYY-MM-DD. match YYYY-MM%
    search_pattern = f"{year}-{month:02d}%"
    cursor.execute('''
        SELECT * FROM expenses WHERE date LIKE ? ORDER BY date DESC
    ''', (search_pattern,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_all_expenses():
    """Fetch all expenses ordered by date."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows
