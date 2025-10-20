import os
import json

def get_data():
    # Construye la ruta correcta al archivo data.json
    script_dir = os.path.dirname(__file__)
    json_path = os.path.abspath(os.path.join(script_dir, "..", "mocks", "data.json"))

    # Abre el archivo y lee los datos
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    return data