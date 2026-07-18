from database.database import SessionLocal
from models.alert import Alert
from models.event import Event


session = SessionLocal()


session.query(Alert).delete()
session.query(Event).delete()


session.commit()

session.close()


print("Base nettoyée")