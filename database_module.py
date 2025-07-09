from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

# === Database Connection ===
def get_db_connection():
    return psycopg2.connect(
        host=st.secrets["connections"]["aurora_db"]["host"],
        database=st.secrets["connections"]["aurora_db"]["database"],
        user=st.secrets["connections"]["aurora_db"]["username"],
        password=st.secrets["connections"]["aurora_db"]["password"],
        cursor_factory=RealDictCursor
    )

def save_results_db(name, pre_score, post_score, timestamp):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            name TEXT,
            pre_score INTEGER,
            post_score INTEGER,
            timestamp TIMESTAMP
        )
    """)
    cur.execute(
        "INSERT INTO results (name, pre_score, post_score, timestamp) VALUES (%s, %s, %s, %s)",
        (name, pre_score, post_score, timestamp)
    )
    conn.commit()
    cur.close()
    conn.close()

def save_user_db(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            login_time TIMESTAMP
        )
    """)
    cur.execute("INSERT INTO users (username, login_time) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING", (username, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()
