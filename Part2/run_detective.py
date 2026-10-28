import sqlite3

conn = sqlite3.connect("sql_detective.db")
with open("sql_detective.sql", encoding="utf-8") as f:
    chunks = f.read().split(";")

lines = []
for chunk in chunks:
    chunk = chunk.strip()
    if not chunk:
        continue
    lines.append(chunk.splitlines()[0])  # the "-- Qn" comment line
    cur = conn.execute(chunk)
    lines.append(str([d[0] for d in cur.description]))
    for row in cur.fetchall():
        lines.append(str(tuple(row)))
    lines.append("")

output = "\n".join(lines)
print(output)

with open("sql_detective_results.txt", "w", encoding="utf-8") as f:
    f.write(output)

#