from models.event import Event
from database.database import SessionLocal
import random
from datetime import datetime



def simulate_attack():


    session = SessionLocal()


    users = [
        "John",
        "Ahmed",
        "Marie"
    ]


    countries = [
        "Russia",
        "China",
        "USA"
    ]


    event = Event(

        user=random.choice(users),

        action="LOGIN",

        location=random.choice(countries),

        hour=random.choice([
            1,
            2,
            3,
            23
        ]),

        status="FAILED"

    )


    session.add(event)

    session.commit()


    session.close()


    return event