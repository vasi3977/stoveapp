import sqlite3

conn = sqlite3.connect('centrala.db')

c = conn.cursor()

c.execute("SELECT * FROM datefunctionare")
items = c.fetchall()
numarMaxim = len(items)
print(numarMaxim)
#url = "DELETE FROM datefunctionare WHERE numar == 60"

#for i in range(1,numarMaxim):
#j = 1
#for item in items:
#	nr = item[0]
#	url2 = "UPDATE datefunctionare SET numar = "+str(j)+ " WHERE numar = " + str(nr)
#	j += 1
#	c.execute(url2)
#

#url2 = "UPDATE datefunctionare SET numar = "+str(23)+ " WHERE numar = " + str(69)
#c.execute(url2)
#for item in items:
#	print(item)

conn.commit()

conn.close()