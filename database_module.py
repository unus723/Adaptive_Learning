import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
import bcrypt

# === DB Connection ===
def get_db_connection():
    return psycopg2.connect(
        host=st.secrets["connections"]["aurora_db"]["host"],
        database=st.secrets["connections"]["aurora_db"]["database"],
        user=st.secrets["connections"]["aurora_db"]["username"],
        password=st.secrets["connections"]["aurora_db"]["password"],
        sslmode="require",
        cursor_factory=RealDictCursor
    )

# === Results Storage ===
def save_results_db(name, pre_score, post_score, username, timestamp):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            name TEXT,
            pre_score INTEGER,
            post_score INTEGER,
            username TEXT NOT NULL,
            timestamp TIMESTAMP
        )
    """)
    cur.execute(
        "INSERT INTO results (name, pre_score, post_score, username, timestamp) VALUES (%s, %s, %s, %s, %s)",
        (name, pre_score, post_score, username, timestamp)
    )
    conn.commit()
    cur.close()
    conn.close()

# === User Management ===
def create_user_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def register_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_pw))
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return bcrypt.checkpw(password.encode(), result['password_hash'].encode())
    return False
