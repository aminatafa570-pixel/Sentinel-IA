from ai.data_loader import DataLoader
from ai.anomaly_detector import AnomalyDetector


# Charger les données
loader = DataLoader()

data = loader.load_events()


print("==========================")
print("DONNEES CHARGEES")
print("==========================")

print(data)


# Création du modèle IA
detector = AnomalyDetector()


print("\n==========================")
print("ENTRAINEMENT IA")
print("==========================")


detector.train(data)


print("Modèle entraîné avec succès")


# Détection
result = detector.predict(data)


print("\n==========================")
print("RESULTAT IA")
print("==========================")


print(result)


