import sys
import os

# Ajouter le dossier principal Sentinel_IA au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from ai.data_loader import DataLoader
from ai.anomaly_detector import AnomalyDetector


print("==========================")
print("CHARGEMENT DES DONNEES")
print("==========================")


loader = DataLoader()

data = loader.load_events()

print(data.head())


print("==========================")
print("ENTRAINEMENT IA")
print("==========================")


detector = AnomalyDetector()

detector.train(data)


print("IA entraînée avec succès")