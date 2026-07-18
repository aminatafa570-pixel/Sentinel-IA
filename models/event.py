from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from database.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)

    # Informations de connexion
    user = Column(String)
    action = Column(String)
    location = Column(String)
    status = Column(String)
    hour = Column(Integer)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Contexte réseau et appareil
    ip_address = Column(String, default="UNKNOWN")
    device = Column(String, default="UNKNOWN")
    network_type = Column(String, default="UNKNOWN")

    # Résultat de l’analyse Sentinel IA
    risk_score = Column(Integer, default=0)
    risk_level = Column(String, default="LOW")
    risk_reasons = Column(Text, default="")
    security_action = Column(String, default="UNKNOWN")