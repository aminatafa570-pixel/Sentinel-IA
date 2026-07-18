from database.database import SessionLocal
from database.models import EventDB, AlertDB



def save_event(event):

    session = SessionLocal()


    new_event = EventDB(

        user=event.user.username,

        action=event.action,

        location=event.location,

        status=event.status

    )


    session.add(new_event)

    session.commit()

    session.close()



def save_alert(alert):

    session = SessionLocal()


    new_alert = AlertDB(

        user=alert.event.user.username,

        level=alert.severity(),

        score=alert.score,

        reason="; ".join(alert.reasons)

    )


    session.add(new_alert)

    session.commit()

    session.close()

