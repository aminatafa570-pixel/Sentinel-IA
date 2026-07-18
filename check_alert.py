import sqlite3


connection = sqlite3.connect("sentinel.db")

cursor = connection.cursor()


cursor.execute("PRAGMA table_info(alerts)")


columns = cursor.fetchall()


print("==========================")
print("COLONNES TABLE ALERTS")
print("==========================")


for column in columns:
    print(column)


connection.close()


