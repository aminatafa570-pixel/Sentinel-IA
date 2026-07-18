from database.database import Base, engine
from models.audit_log import AuditLog

Base.metadata.create_all(engine)

print("Migration V3 terminée : table audit_logs créée.")