import os
import sqlite3

DB = "sql_detective.db"

if os.path.exists(DB):
    os.remove(DB)

conn = sqlite3.connect(DB)
with open("sql_detective_data.sql", encoding="utf-8") as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print("Loaded sql_detective.db")