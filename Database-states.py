import sqlite3
conn = sqlite3.connect('PieMessageStates.db')


c = conn.cursor()
c.execute('''CREATE TABLE clients
          (Username text, Publickey text, Phone text, Email Text, Messages Text)''')

conn.commit()
conn.close()

