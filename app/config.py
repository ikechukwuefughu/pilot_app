# import sqlite3

# DATABASE = r"C:\Users\User\Downloads\Yittbox Python Projects\myenv\fiona_pilot_app\creche.db"

# def get_db_connection():
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row
#     conn.execute("PRAGMA foreign_keys = ON;")
#     return conn

import sqlite3

DATABASE = r"C:\Users\User\Downloads\Yittbox Python Projects\myenv\fiona_pilot_app\creche.db"

def get_db_connection():
    conn = sqlite3.connect(
        DATABASE,
        timeout=5,              # wait up to 5 seconds for locks instead of failing immediately
        check_same_thread=False # avoids thread errors with Flask’s threaded server
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    # Optional but recommended: enable WAL mode (you can also do this once at init)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn
