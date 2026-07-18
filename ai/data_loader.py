from database.database import SessionLocal
from models.event import Event

import pandas as pd


class DataLoader:


    def load_events(self):

        session = SessionLocal()


        events = session.query(Event).all()


        data = []


        for event in events:


            data.append({

                "hour": event.hour,


                "failed_login":
                    1 if event.status == "FAILED" else 0,


                "foreign_location":
                    1 if event.location not in [
                        "Senegal",
                        "France"
                    ] else 0

            })


        session.close()


        return pd.DataFrame(data)