class Analyzer:
    

    def analyze(self, event):

        score = 0

        reasons = []


        # Vérification de l'heure

        if event.hour < 6:

            score += 30
            reasons.append(
                "Connexion à une heure inhabituelle"
            )


        # Vérification des échecs

        if event.status == "FAILED":

            score += 40
            reasons.append(
                "Tentative de connexion échouée"
            )


        # Vérification localisation

        if event.location != event.user.country:

            score += 30
            reasons.append(
                "Localisation inhabituelle"
            )


        return score, reasons

