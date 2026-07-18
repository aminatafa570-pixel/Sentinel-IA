import pandas as pd

from ai.anomaly_detector import AnomalyDetector



class AIPredictor:


    def __init__(self):

        self.detector = AnomalyDetector()


        try:

            self.detector.load_model(
                "sentinel_model.pkl"
            )

            print(
                "Modèle IA chargé avec succès"
            )


        except Exception as e:

            print(
                "Erreur chargement modèle IA :",
                e
            )



    def analyze(self, event):


        dataframe = pd.DataFrame([{

            "hour": event.hour,


            "failed_login":
                1 if event.status == "FAILED" else 0,


            "foreign_location":
                1 if event.location not in [
                    "Senegal",
                    "France"
                ] else 0

        }])


        result = self.detector.predict(
            dataframe
        )


        prediction = result[
            "ai_prediction"
        ].iloc[0]


        return prediction == -1