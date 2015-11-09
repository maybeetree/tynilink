import MySQLdb as mdb
import base64
from hashlib import sha1

conc = mdb.connect('localhost', 'root', 'password', 'shortener_urls')
curc = conc.cursor()

curc.execute("DROP TABLE IF EXISTS urls") #drop table if exists
curc.execute("CREATE TABLE urls(Id INT PRIMARY KEY AUTO_INCREMENT, \
shorturl VARCHAR(20), longurl VARCHAR(325), pass VARCHAR(41), \
owner VARCHAR(10))")   #re-make table

google = 'http://www.google.com'
besthash = 'http://www.peterbe.com/plog/best-hashing-function-in-python'
isa = 'http://www.isa.nl'

#If you do not want password, make it '' or don't specify
curc.execute("INSERT INTO urls(shorturl,longurl,pass,owner) \
VALUES('gug','%s','','Nikita')" % google)

curc.execute("INSERT INTO urls(shorturl,longurl,owner) \
VALUES('tehbesthashes','%s','Jhon')" % besthash)

#passworded link
curc.execute("INSERT INTO urls(shorturl,longurl,pass,owner) \
VALUES('igh','%s','%s','Fred_Fuchs')" % (isa, sha1(b'hello').hexdigest()))

curc.execute("SELECT * FROM urls")
print(curc.fetchall())
#print(dir(curc))

conc.commit()

curc.close()
conc.close()
