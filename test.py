import sqlite3

conn = sqlite3.connect('centrala.db')

c = conn.cursor()

#c.execute("""CREATE TABLE datefunctionare(
#	numar int,
#	data_pornire text,
#	data_oprire text,
#	timp_functionare text
#)""")

#c.execute("INSERT INTO datefunctionare VALUES (1, datetime('now'), datetime('now'), '')")
#statusCentrala = 'Stabil'
#url = "UPDATE datefunctionare SET data_oprire = datetime('now') WHERE numar = " + str(1)
#url = "DELETE FROM datefunctionare"
#c.execute(url)
c.execute("SELECT * FROM functionare")
items = c.fetchall()

for item in items:
	print(item)

conn.commit()

conn.close()
