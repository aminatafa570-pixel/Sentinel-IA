from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from database.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    alert_id = Column(Integer)

    title = Column(String)
    severity = Column(String)
    status = Column(String, default="NEW")
    assigned_to = Column(String, default="Unassigned")

    description = Column(Text, default="")
    comments = Column(Text, default="")

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)