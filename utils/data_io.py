import os
import json

def read_json(path):
    with open(path) as f:
        file = json.load(f)
    return file

def write_json(path, file):
    os.makedirs(os.path.split(path)[0], exist_ok=True)
    with open(path, 'w+') as f:
        json.dump(file, f)
