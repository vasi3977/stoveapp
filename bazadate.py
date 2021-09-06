import sqlite3

conn = sqlite3.connect('centrala.db')

c = conn.cursor()

c.execute("SELECT sql FROM sqlite_master WHERE name = 'functionare'")#show table structure
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")#show database content
items = c.fetchall()

for item in items:
	print(item)
	sql = "SELECT sql FROM sqlite_master WHERE name = '" + str(item[0]) + "'"
	#print(sql)
	c.execute(sql)
	baze = c.fetchall()
	for baza in baze:
		print(baza)
	

conn.commit()

conn.close()