import sqlite3
conn = sqlite3.connect('PieMessage.db')


c = conn.cursor()
c.execute('''CREATE TABLE clients
          (CID text, KEY text, ONLINE integer)''')

conn.commit()
conn.close()

