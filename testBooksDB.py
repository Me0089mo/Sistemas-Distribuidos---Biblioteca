import sys
sys.path.append(".")
from BooksDB_Connection import BooksDB_Connection

db = BooksDB_Connection()
db.newSession('16:50:25')
db.userExists(['11.29.84.72', '1546'])
db.getBook(8, ['11.29.84.72', '1546'], '16:51:08')
db.closeSession('16:52:30')
db.closeConnection()
db.openConnection()
db.newSession('16:55:40')
db.userExists(['11.29.84.72', '4865'])
db.getBook(8, ['11.29.84.72', '4865'], '16:57:36')
db.userExists(['48.110.34.93', '56471'])
db.getBook(8, ['48.110.34.93', '56471'], '16:58:24')
db.closeSession('17:01:09')