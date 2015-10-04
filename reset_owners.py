import MySQLdb

concs = MySQLdb.connect('localhost', 'root', 'password', 'shortener_urls')
curcs = concs.cursor()

curcs.execute("DROP TABLE IF EXISTS owners") #drop table if exists
curcs.execute("CREATE TABLE owners(Id INT PRIMARY KEY AUTO_INCREMENT, \
name VARCHAR(10), password VARCHAR(10))")   #re-make table

curcs.execute("INSERT INTO owners(name,password) \
VALUES('','')")   #for non-owner urls

curcs.execute("INSERT INTO owners(name,password) \
VALUES('Jhon','Jhon')")

curcs.execute("INSERT INTO owners(name,password) \
VALUES('Fred_Fuchs','Fred_Fuchs')")

curcs.execute("SELECT * FROM owners")
print(curcs.fetchall())
#print(dir(curc))

concs.commit()

curcs.close()
concs.close()

