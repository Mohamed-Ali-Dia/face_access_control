# models.py
import sqlite3
import pickle
import hashlib

DB_FILE = "users.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()

        # --------------------
        # Table des employés
        # --------------------
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                encoding BLOB NOT NULL
            )
        ''')

        # --------------------
        # Table des comptes
        # --------------------
        c.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'gardien'))
            )
        ''')

        # --------------------
        # Table des sessions
        # --------------------
        c.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # --------------------
        # Créer un compte admin par défaut si inexistant
        # --------------------
        c.execute("SELECT * FROM accounts WHERE username = 'admin'")
        if not c.fetchone():
            c.execute(
                "INSERT INTO accounts (username, password, role) VALUES (?, ?, ?)",
                ("admin", hash_password("admin101855"), "admin")
            )

        conn.commit()

# --------------------
# Gestion employés
# --------------------
def add_user(name, encoding, photo_bytes=None):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (name, encoding, photo) VALUES (?, ?, ?)",
            (name, pickle.dumps(encoding), photo_bytes)
        )
        conn.commit()


def update_user_name(old_name, new_name):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET name = ? WHERE name = ?", (new_name, old_name))
        conn.commit()


def update_user_encoding(name, new_encoding):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET encoding = ? WHERE name = ?", (pickle.dumps(new_encoding), name))
        conn.commit()


def update_user_photo(name, photo_bytes):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET photo = ? WHERE name = ?", (photo_bytes, name))
        conn.commit()


def delete_user(name):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE name = ?", (name,))
        conn.commit()


def get_all_users():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT name, encoding, photo FROM users")
        return [(row[0], pickle.loads(row[1]), row[2]) for row in c.fetchall()]

# --------------------
# Gestion comptes
# --------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def add_account(username, password, role):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO accounts (username, password, role) VALUES (?, ?, ?)",
                  (username, hash_password(password), role))
        conn.commit()


def authenticate(username, password):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT password, role FROM accounts WHERE username = ?", (username,))
        row = c.fetchone()
        if row and row[0] == hash_password(password):
            return True, row[1]
        return False, None


def get_all_accounts():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT username, role FROM accounts")
        return c.fetchall()


def get_account_by_username(username):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM accounts WHERE username = ?", (username,))
        row = c.fetchone()
        return row[0] if row else None


def update_account(username, new_password=None, new_role=None):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        if new_password and new_role:
            c.execute(
                "UPDATE accounts SET password = ?, role = ? WHERE username = ?",
                (hash_password(new_password), new_role, username)
            )
        elif new_password:
            c.execute(
                "UPDATE accounts SET password = ? WHERE username = ?",
                (hash_password(new_password), username)
            )
        elif new_role:
            c.execute(
                "UPDATE accounts SET role = ? WHERE username = ?",
                (new_role, username)
            )
        conn.commit()


def update_account_password(username, new_password):
    update_account(username, new_password=new_password)


def delete_account(username):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM accounts WHERE username = ?", (username,))
        conn.commit()


# --------------------
# Gestion des sessions
# --------------------
def create_session(username, role):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM sessions")  # Supprime session précédente
        c.execute("INSERT INTO sessions (username, role) VALUES (?, ?)", (username, role))
        conn.commit()


def get_session():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT username, role FROM sessions LIMIT 1")
        row = c.fetchone()
        return (row[0], row[1]) if row else (None, None)


def delete_session():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM sessions")
        conn.commit()