import sqlite3

conn = sqlite3.connect('centrala.db')

c = conn.cursor()

c.execute("SELECT * FROM functionare")
items = c.fetchall()

for item in items:
	print(item)

conn.commit()

conn.close()