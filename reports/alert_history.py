from database.database import SessionLocal
from models.alert import Alert



class AlertHistory:


    def __init__(self):

        self.session = SessionLocal()



    def get_all_alerts(self):

        alerts = self.session.query(Alert).all()

        return alerts



    def display(self):


        alerts = self.get_all_alerts()


        print("\n==============================")
        print(" HISTORIQUE DES ALERTES ")
        print("==============================")



        if len(alerts) == 0:

            print("Aucune alerte détectée.")

            return



        print(
            "Nombre total d'alertes :",
            len(alerts)
        )



        for alert in alerts:


            print("\n------------------------------")

            print(
                "Utilisateur :",
                alert.user
            )


            print(
                "Niveau :",
                alert.level
            )


            print(
                "Score :",
                alert.score,
                "/100"
            )


            print(
                "Raison :",
                alert.reason
            )



    def close(self):

        self.session.close()