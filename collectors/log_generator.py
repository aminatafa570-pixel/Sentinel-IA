import random
from datetime import datetime

from models.event import Event


class LogGenerator:


    def __init__(self):

        self.users = [
            "Ahmed",
            "Marie",
            "John"
        ]

        self.locations = [
            "Senegal",
            "France",
            "USA",
            "China",
            "Russia"
        ]



    def generate_event(self):

        user = random.choice(self.users)

        action = "LOGIN"

        location = random.choice(self.locations)

        hour = random.randint(0, 23)


        # Génération intelligente des comportements

        if location in ["Senegal", "France"]:

            status = random.choice(
                [
                    "SUCCESS",
                    "SUCCESS",
                    "SUCCESS"
                ]
            )

        else:

            status = random.choice(
                [
                    "FAILED",
                    "FAILED",
                    "SUCCESS"
                ]
            )



        event = Event(

            user=user,

            action=action,

            location=location,

            hour=hour,

            status=status
        )


        return event

