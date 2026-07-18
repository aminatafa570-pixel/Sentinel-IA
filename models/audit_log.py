from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    actor = Column(String)
    action = Column(String)
    target_type = Column(String)
    target_id = Column(Integer)
    details = Column(Text)