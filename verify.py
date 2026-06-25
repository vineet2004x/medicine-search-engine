import sqlite3

conn = sqlite3.connect("medicines.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM Medicines")
print(cursor.fetchone())

conn.close()