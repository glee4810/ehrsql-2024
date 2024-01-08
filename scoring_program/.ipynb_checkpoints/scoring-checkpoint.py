import json
import os
import sys
import time
import sqlite3
import numpy as np
import pandas as pd
from reliability_score import calculate_score
from postprocessing import post_process_sql

reference_dir = os.path.join(sys.argv[1], 'ref')
prediction_dir = os.path.join(sys.argv[1], 'res')
score_dir = sys.argv[2]

print('Load Data')
with open(os.path.join(reference_dir, 'label.json')) as f:
    truth = json.load(f)
with open(os.path.join(prediction_dir, 'prediction.json')) as f:
    prediction = json.load(f)

print('Checking Accuracy')
start = time.time()
real_dict = {id_: post_process_sql(truth[id_]) for id_ in truth}
pred_dict = {id_: post_process_sql(prediction[id_]) for id_ in prediction}
accuracy0, accuracy10, accuracyN = calculate_score(real_dict, pred_dict)
duration = time.time() - start
print('Scores:')
scores = {
    'accuracy0': accuracy0,
    'accuracy10': accuracy10,
    'accuracyN': accuracyN
}
print(scores)

with open(os.path.join(score_dir, 'scores.json'), 'w') as score_file:
    score_file.write(json.dumps(scores))