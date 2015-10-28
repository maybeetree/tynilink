import MySQLdb

concs = MySQLdb.connect('localhost', 'root', 'password', 'shortener_urls')
curcs = concs.cursor()

curcs.execute("DROP TABLE IF EXISTS url_views") #drop table if exists
curcs.execute("CREATE TABLE url_views(\
Id INT PRIMARY KEY AUTO_INCREMENT, \
urlid INT, \
ip VARCHAR(15), \
country_code VARCHAR(6), \
country_name VARCHAR(48), \
region_code VARCHAR(10), \
region_name VARCHAR(176), \
city VARCHAR(176), \
zip_code VARCHAR(17), \
time_zone VARCHAR(20), \
latitude FLOAT, \
longitude FLOAT, \
metro_code INT, \
date VARCHAR(24))")   #re-make table

curcs.execute("INSERT INTO url_views (urlid, ip) VALUES (1, '127.0.0.1')")

concs.commit()
