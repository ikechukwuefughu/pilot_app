import sqlite3

conn = sqlite3.connect("creche.db")
cursor = conn.cursor()

cursor.execute("""

CREATE TABLE "parent" (
	"created_at"	TEXT DEFAULT (datetime('now')),
	"parent_id"	INTEGER,
	"household_id"	INTEGER,
	"first_name"	TEXT,
	"last_name"	TEXT,
	"phone"	TEXT,
	"email"	TEXT,
	PRIMARY KEY("parent_id" AUTOINCREMENT),
	FOREIGN KEY("household_id") REFERENCES "household"("household_id")
);
""")

conn.commit()
conn.close()