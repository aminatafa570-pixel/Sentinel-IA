from sklearn.ensemble import IsolationForest
import pickle


class AnomalyDetector:


    def __init__(self):

        self.model = IsolationForest(
            n_estimators=200,
            contamination=0.10,
            random_state=42
        )

        self.trained = False



    def train(self, dataframe):

        X = dataframe[
            [
                "hour",
                "failed_login",
                "foreign_location"
            ]
        ]


        self.model.fit(X)

        self.trained = True


        # sauvegarde du modèle
        self.save_model("sentinel_model.pkl")



    def predict(self, dataframe):

        if not self.trained:
            raise Exception(
                "Le modèle IA n'est pas chargé."
            )


        X = dataframe[
            [
                "hour",
                "failed_login",
                "foreign_location"
            ]
        ]


        prediction = self.model.predict(X)

        dataframe["ai_prediction"] = prediction

        return dataframe



    def save_model(self, filename):

        with open(filename, "wb") as file:

            pickle.dump(
                self.model,
                file
            )


        print(
            "Modèle sauvegardé dans :",
            filename
        )



    def load_model(self, filename):

        with open(filename, "rb") as file:

            self.model = pickle.load(file)


        self.trained = True