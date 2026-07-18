import sqlite3


EVENT_COLUMNS = {
    "timestamp": "DATETIME",
    "ip_address": "VARCHAR",
    "device": "VARCHAR",
    "network_type": "VARCHAR",
    "risk_score": "INTEGER",
    "risk_level": "VARCHAR",
    "risk_reasons": "TEXT",
}

ALERT_COLUMNS = {
    "event_id": "INTEGER",
    "status": "VARCHAR DEFAULT 'OPEN'",
    "created_at": "DATETIME",
}


def add_missing_columns(cursor, table_name, columns):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {column[1] for column in cursor.fetchall()}

    for column_name, column_definition in columns.items():
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE {table_name} "
                f"ADD COLUMN {column_name} {column_definition}"
            )
            print(f"Colonne ajoutée : {table_name}.{column_name}")


connection = sqlite3.connect("sentinel.db")
cursor = connection.cursor()

add_missing_columns(cursor, "events", EVENT_COLUMNS)
add_missing_columns(cursor, "alerts", ALERT_COLUMNS)

cursor.execute(
    """
    UPDATE events
    SET security_action = 'UNKNOWN'
    WHERE security_action IS NULL
    """
)

connection.commit()
connection.close()

print("Migration Sentinel V1 terminée avec succès.")