import db

conn = db.get_conn()
cur = conn.cursor()
cur.execute("SHOW TABLES")
print([row[0] for row in cur.fetchall()])