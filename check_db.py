import sqlite3


connection = sqlite3.connect("sentinel.db")

cursor = connection.cursor()



print("==========================")
print("DERNIERS EVENEMENTS")
print("==========================")


cursor.execute("""
SELECT id, user, action, location, status, hour
FROM events
ORDER BY id DESC
LIMIT 10
""")


events = cursor.fetchall()



for event in events:

    print(
        "ID :", event[0],
        "| User :", event[1],
        "| Action :", event[2],
        "| Location :", event[3],
        "| Status :", event[4],
        "| Hour :", event[5]
    )



print("\n==========================")
print("NOMBRE TOTAL EVENEMENTS")
print("==========================")


cursor.execute("""
SELECT COUNT(*)
FROM events
""")


count = cursor.fetchone()[0]


print("Total :", count)



connection.close()