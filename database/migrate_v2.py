from database.database import Base, engine
from models.incident import Incident

Base.metadata.create_all(engine)

print("Migration V2 terminée : table incidents créée.")