import MySQLdb
from hashlib import sha1

concs = MySQLdb.connect('localhost', 'root', 'password', 'shortener_urls')
curcs = concs.cursor()

curcs.execute("DROP TABLE IF EXISTS owners") #drop table if exists
curcs.execute("CREATE TABLE owners(Id INT PRIMARY KEY AUTO_INCREMENT, \
name VARCHAR(10), password VARCHAR(41), email VARCHAR(30))")   #re-make table

curcs.execute("INSERT INTO owners(name,password,email) \
VALUES('','%s','no@email.com')" % sha1(b'').hexdigest())
# this is for url that do not belong to anyone.

curcs.execute("INSERT INTO owners(name,password,email) \
VALUES('alex','%s','asoshnin@gmail.com')" % sha1(b'pass').hexdigest())

curcs.execute("INSERT INTO owners(name,password,email) \
VALUES('Fred_Fuchs','%s','fred@mail.com')" % sha1(b'Fred_Fuchs').hexdigest())

curcs.execute("SELECT * FROM owners")
print(curcs.fetchall())
#print(dir(curc))

concs.commit()

curcs.close()
concs.close()

