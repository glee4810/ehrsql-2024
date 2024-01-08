import json
import os
import sys
import numpy as np
from data_io import read_json, write_json

input_dir = os.path.abspath(sys.argv[1])
output_dir = os.path.abspath(sys.argv[2])
program_dir = os.path.abspath(sys.argv[3])
submission_dir = os.path.abspath(sys.argv[4])

def find_json_file(path):
    json_file = []
    for file in os.listdir(path):
        if file.endswith('.json'):
            json_file.append(file)
    assert len(json_file)==1, 'Submit only one json file'
    return json_file[0]

def main():
    print('Reading Prediction')
    submission_file_path = find_json_file(submission_dir)
    prediction = read_json(os.path.join(submission_dir, submission_file_path))
    write_json(prediction, os.path.join(output_dir, 'prediction.json'))

if __name__ == '__main__':
    main()
