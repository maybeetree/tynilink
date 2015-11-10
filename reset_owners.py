import MySQLdb
from hashlib import sha1

concs = MySQLdb.connect('localhost', 'root', 'password', 'shortener_urls')
curcs = concs.cursor()

curcs.execute("DROP TABLE IF EXISTS owners") #drop table if exists
curcs.execute("CREATE TABLE owners(Id INT PRIMARY KEY AUTO_INCREMENT, \
name VARCHAR(30), password VARCHAR(41), perm INT, email VARCHAR(30))")
#re-make table

#perm lvl 0 = basic user. create, modify, delete links
#perm lvl 1 = Supporter. basic + change MOTD
#perm lvl 2 = admin. Root acess

curcs.execute("INSERT INTO owners(name,password,perm,email) \
VALUES('','%s',0,'no@email.com')" % sha1(b'').hexdigest())
# this is for url that do not belong to anyone.

curcs.execute("INSERT INTO owners(name,password,perm,email) \
VALUES('MaybE_Tree','%s',2,'asoshnin@gmail.com')" % sha1(b'noend').hexdigest())

curcs.execute("INSERT INTO owners(name,password,perm,email) \
VALUES('Fred_Fuchs','%s',0,'fred@mail.com')" % sha1(b'Fred_Fuchs').hexdigest())

curcs.execute("SELECT * FROM owners")
print(curcs.fetchall())
#print(dir(curc))

concs.commit()

curcs.close()
concs.close()

