import os

folders = [
    "NeuroAR",
    "NeuroAR/Scripts",
    "NeuroAR/Scripts/Network",
    "NeuroAR/Scripts/AR",
    "NeuroAR/Scripts/Communication",
    "NeuroAR/Scripts/UI",
    "NeuroAR/Prefabs",
    "NeuroAR/Materials",
    "NeuroAR/Shaders",
    "NeuroAR/Scenes"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Créé : {folder}")

print("Structure NeuroAR créée avec succès.")