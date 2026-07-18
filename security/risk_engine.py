from ai.predictor import AIPredictor


class RiskEngine:


    def __init__(self):

        self.ai = AIPredictor()



    def analyze(self, event):

        score = 0
        reasons = []


        # Connexion échouée

        if event.status == "FAILED":

            score += 40

            reasons.append(
                "Tentative de connexion échouée"
            )



        # Heure inhabituelle

        if event.hour < 6 or event.hour > 22:

            score += 30

            reasons.append(
                "Connexion à une heure inhabituelle"
            )



        # Localisation inhabituelle

        if event.location not in [
            "Senegal",
            "France"
        ]:

            score += 30

            reasons.append(
                "Localisation inhabituelle"
            )



               # IA : signal complémentaire, sans compter deux fois
        # les mêmes critères que les règles de sécurité.
        if self.ai.analyze(event):
            score += 10
            reasons.append(
                "Anomalie comportementale détectée par Sentinel IA"
            )

        if score > 100:
            score = 100

        reasons = list(dict.fromkeys(reasons))

        # Décision Sentinel IA
        if score < 25:
            decision = "ALLOWED"
        elif score < 50:
            decision = "MFA_REQUIRED"
        elif score < 75:
            decision = "TEMP_BLOCK"
        else:
            decision = "BLOCKED"

        # Niveau de gravité
        if score >= 75:
            level = "CRITICAL"
        elif score >= 50:
            level = "HIGH"
        elif score >= 25:
            level = "MEDIUM"
        else:
            level = "LOW"

        # ==========================
        # DECISION SENTINEL
        # ==========================


        if score < 30:

            decision = "ALLOWED"


        elif score < 60:

            decision = "MFA_REQUIRED"


        elif score < 80:

            decision = "TEMP_BLOCK"


        else:

            decision = "BLOCKED"



        # Niveau

        if score >= 80:

            level = "CRITICAL"


        elif score >= 60:

            level = "HIGH"


        elif score >= 30:

            level = "MEDIUM"


        else:

            level = "LOW"



        return {

            "score": score,

            "level": level,

            "decision": decision,

            "reasons": reasons

        }