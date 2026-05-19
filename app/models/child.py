import sqlite3

conn = sqlite3.connect("creche.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS child (
    created_at TEXT DEFAULT (datetime('now')),
    child_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    date_of_birth TEXT,
    ppsn TEXT NOT NULL,
    ecce_eligible INTEGER NOT NULL CHECK (ecce_eligible IN (0, 1)),
    start_date TEXT,
    end_date TEXT,
    FOREIGN KEY (household_id) REFERENCES household (household_id)
);
""")

conn.commit()
conn.close()