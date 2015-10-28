import MySQLdb

concs = MySQLdb.connect('localhost', 'root', 'password', 'shortener_urls')
curcs = concs.cursor()

curcs.execute("DROP TABLE IF EXISTS owners") #drop table if exists
curcs.execute("CREATE TABLE owners(Id INT PRIMARY KEY AUTO_INCREMENT, \
name VARCHAR(10), password VARCHAR(10), email VARCHAR(30))")   #re-make table

curcs.execute("INSERT INTO owners(name,password,email) \
VALUES('tree','jkl','no@email.com')")

curcs.execute("INSERT INTO owners(name,password,email) \
VALUES('alex','lgfh','asoshnin@gmail.com')")

curcs.execute("INSERT INTO owners(name,password,email) \
VALUES('Fred_Fuchs','Fred_Fuchs','fred@mail.com')")

curcs.execute("SELECT * FROM owners")
print(curcs.fetchall())
#print(dir(curc))

concs.commit()

curcs.close()
concs.close()

