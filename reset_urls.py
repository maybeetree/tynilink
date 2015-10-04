import MySQLdb as mdb
import base64

conc = mdb.connect('localhost', 'root', 'password', 'shortener_urls')
curc = conc.cursor()

curc.execute("DROP TABLE IF EXISTS urls") #drop table if exists
curc.execute("CREATE TABLE urls(Id INT PRIMARY KEY AUTO_INCREMENT, \
shorturl VARCHAR(20), longurl VARCHAR(325), pass VARCHAR(10), \
owner VARCHAR(10))")   #re-make table

google = base64.b64encode('http://www.google.com')
besthash = base64.b64encode('http://www.peterbe.com/plog/best-hashing-function-in-python')
isa = base64.b64encode('http://www.isa.nl')#all urls must be base 64 encoded

#If you do not want password, make it '' or don't specify
curc.execute("INSERT INTO urls(shorturl,longurl,pass,owner) \
VALUES('gug','%s','','Nikita')" % google)

curc.execute("INSERT INTO urls(shorturl,longurl,owner) \
VALUES('tehbesthashes','%s','Jhon')" % besthash)

#password link
curc.execute("INSERT INTO urls(shorturl,longurl,pass,owner) \
VALUES('igh','%s','hello','Fred_Fuchs')" % isa)

curc.execute("SELECT * FROM urls")
print(curc.fetchall())
#print(dir(curc))

conc.commit()

curc.close()
conc.close()
