#!/usr/bin/env python3
from database import MySQLdb
db = MySQLdb()
db.dbhost = "localhost"
db.dbuser = "Monitoring"
db.dbpassword = "tlA7bPv2qLVLwG0r"
db.db = "Monitoring"
sqlquery = "select * from Hosts;"
result = db.Query(sqlquery)
print (result)

