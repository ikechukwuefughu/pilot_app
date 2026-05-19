import sqlite3

conn = sqlite3.connect("creche.db")
cursor = conn.cursor()

cursor.execute("""

CREATE TABLE "household" (
	"created_at"	TEXT DEFAULT (datetime('now')),
	"household_id"	INTEGER,
	"household_name"	TEXT,
	"address_line1"	TEXT,
	"address_line2"	TEXT,
	"city"	TEXT,
	"county"	TEXT,
	"eircode"	TEXT,
	"phone"	TEXT,
	PRIMARY KEY("household_id" AUTOINCREMENT)
);
""")

conn.commit()
conn.close()