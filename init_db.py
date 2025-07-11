from database_module import get_db_connection

# === One-Time Table Initialization Script ===
def initialize_tables():
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            name TEXT,
            pre_score INTEGER,
            post_score INTEGER,
            timestamp TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tables initialized successfully.")

if __name__ == "__main__":
    initialize_tables()
