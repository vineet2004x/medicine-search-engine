import sqlite3

conn = sqlite3.connect("medicines.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(Medicines)")

for column in cursor.fetchall():
    print(column)

conn.close()