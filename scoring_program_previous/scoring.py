import json
import os
import sys
import sqlite3
import numpy as np
import pandas as pd
from reliability_score import calculate_score, penalize
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
real_dict = {id_: post_process_sql(truth[id_]) for id_ in truth}
pred_dict = {id_: post_process_sql(prediction[id_]) for id_ in prediction}
assert set(real_dict) == set(pred_dict), "IDs do not match"

scores = calculate_score(real_dict, pred_dict)
accuracy0 = penalize(scores, penalty=0)
accuracy5 = penalize(scores, penalty=5)
accuracy10 = penalize(scores, penalty=10)
accuracyN = penalize(scores, penalty=len(scores))

print('Scores:')
scores_dict = {
    'accuracy0': accuracy0*100,
    'accuracy5': accuracy5*100,    
    'accuracy10': accuracy10*100,
    'accuracyN': accuracyN*100
}
print(scores_dict)

with open(os.path.join(score_dir, 'scores.json'), 'w') as score_file:
    score_file.write(json.dumps(scores_dict))