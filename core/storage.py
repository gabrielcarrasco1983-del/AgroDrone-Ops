import json
import os

DRONES_FILE = "drones.json"

def load_drones():
    """Carga la base de datos de drones desde el archivo JSON."""
    if not os.path.exists(DRONES_FILE):
        return {}
    try:
        with open(DRONES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_drones(drones_dict):
    """Guarda la configuración de los drones en el archivo JSON."""
    try:
        with open(DRONES_FILE, "w", encoding="utf-8") as f:
            json.dump(drones_dict, f, indent=4)
    except Exception as e:
        print(f"Error al guardar: {e}")
