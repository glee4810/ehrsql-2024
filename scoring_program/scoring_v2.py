import json
import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import multiprocessing as mp
from scoring_utils import process_answer, reliability_score, penalize


reference_dir = os.path.join(sys.argv[1], 'ref')
prediction_dir = os.path.join(sys.argv[1], 'res')
score_dir = sys.argv[2]


print('Load Data')
with open(os.path.join(reference_dir, 'answer.json')) as f: # gt SQL query
    real_dict = json.load(f)
with open(os.path.join(prediction_dir, 'prediction.json')) as f: # retrived answer (not SQL query)
    pred_dict = json.load(f)
assert set(real_dict) == set(pred_dict), "IDs do not match"


# preprocess predicted answer to match the format as GT answer
real_result = {}
for key in real_dict:
    if real_dict[key] != 'null':
        real_result[key] = process_answer(real_dict[key])
    else:
        real_result[key] = real_dict[key]
pred_result = {}
for key in pred_dict:
    if pred_dict[key] != 'null':
        pred_result[key] = process_answer(pred_dict[key])
    else:
        pred_result[key] = pred_dict[key]


print('Checking Accuracy')
scores = reliability_score(real_result, pred_result)
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