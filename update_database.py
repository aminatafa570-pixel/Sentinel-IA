import sqlite3


connection = sqlite3.connect("sentinel.db")

cursor = connection.cursor()


cursor.execute("""
PRAGMA table_info(events)
""")


columns = [
    c[1]
    for c in cursor.fetchall()
]


if "security_action" not in columns:

    cursor.execute("""
    ALTER TABLE events
    ADD COLUMN security_action VARCHAR DEFAULT 'ALLOWED'
    """)

    print("Colonne ajoutée")

else:

    print("Colonne déjà présente")



connection.commit()

connection.close()


print("Base mise à jour")