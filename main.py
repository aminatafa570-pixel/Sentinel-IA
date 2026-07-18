from database.database import engine, Base, SessionLocal

from collectors.log_generator import LogGenerator

from models.alert import Alert

from security.risk_engine import RiskEngine



# Création des tables
Base.metadata.create_all(engine)


# Session base de données
session = SessionLocal()


# Générateur d'événements
generator = LogGenerator()


# Moteur complet (règles + IA)
risk_engine = RiskEngine()



for i in range(20):


    # Génération événement
    event = generator.generate_event()



    # Sauvegarde événement
    session.add(event)

    session.commit()



    # Analyse sécurité complète
    # (règles + intelligence artificielle)
    analysis = risk_engine.analyze(event)



    score = analysis["score"]

    level = analysis["level"]

    reasons = analysis["reasons"]



    # Suppression des doublons
    reasons = list(dict.fromkeys(reasons))



    print("\n==========================")
    print("Nouvel événement détecté")
    print("==========================")


    print("Utilisateur :", event.user)

    print("Action :", event.action)

    print("Lieu :", event.location)

    print("Heure :", event.hour)

    print("Résultat :", event.status)

    print("Score risque :", score, "/100")



    # Création alerte

    if score >= 70:


        alert = Alert(

            user=event.user,

            level=level,

            score=score,

            reason="; ".join(reasons)

        )


        session.add(alert)

        session.commit()



        print("\n==============================")

        print("🚨 SENTINEL AI ALERT")

        print("==============================")


        print("Utilisateur :", event.user)

        print("Type :", event.action)

        print("Niveau :", level)

        print("Score de risque :", score, "/100")



        print("\nRaisons :")


        for reason in reasons:

            print("-", reason)



        print("\nStatut : OPEN")



session.close()