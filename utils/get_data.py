import json

def get_data():
    with open('mocks/data.json', 'r') as file:
      data = json.load(file)
    return data