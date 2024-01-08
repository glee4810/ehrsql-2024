import json

def read_json(path):
    with open(path) as f:
        file = json.load(f)
    return file

def write_json(path, file):
    with open(path, 'w+') as f:
        json.dump(file, f)
