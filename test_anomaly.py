from ai.data_loader import DataLoader
from ai.anomaly_detector import AnomalyDetector


# Charger les événements
loader = DataLoader()

data = loader.load_events()


print("==========================")
print("DONNEES")
print("==========================")

print(data.head())


# Création IA
detector = AnomalyDetector()


# Entrainement
detector.train(data)


# Test
result = detector.predict(data)


print("==========================")
print("RESULTAT IA")
print("==========================")

print(result)