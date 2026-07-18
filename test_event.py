from database.database import SessionLocal
from models.event import Event


session = SessionLocal()


event = session.query(Event).first()


print(event.__dict__)


session.close()