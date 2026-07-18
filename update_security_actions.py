import sqlite3


connection = sqlite3.connect("sentinel.db")

cursor = connection.cursor()


cursor.execute("""
SELECT id, status
FROM events
""")


events = cursor.fetchall()


for event in events:

    event_id = event[0]
    status = event[1]


    if status == "FAILED":

        decision = "BLOCKED"


    else:

        decision = "ALLOWED"



    cursor.execute("""
    UPDATE events
    SET security_action = ?
    WHERE id = ?
    """,
    (
        decision,
        event_id
    ))



connection.commit()

connection.close()


print("✅ Décisions Sentinel ajoutées aux anciens événements")