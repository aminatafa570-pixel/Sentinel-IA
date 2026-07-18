from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from database.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer)

    user = Column(String)
    level = Column(String)
    score = Column(Integer)
    reason = Column(Text)

    status = Column(String, default="OPEN")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )