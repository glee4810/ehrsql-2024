# Official metric for the EHRSQL shared task 2024

import json
import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import multiprocessing as mp
from scoring_utils import reliability_score, penalize
from postprocessing import post_process_sql


reference_dir = os.path.join(sys.argv[1], 'ref')
prediction_dir = os.path.join(sys.argv[1], 'res')
score_dir = sys.argv[2]


print('Load Data')
with open(os.path.join(reference_dir, 'label.json')) as f:
    real_dict = json.load(f)
with open(os.path.join(prediction_dir, 'prediction.json')) as f:
    pred_dict = json.load(f)
assert set(real_dict) == set(pred_dict), "IDs do not match"


print('Executing Queries')
real_dict = {id_: post_process_sql(real_dict[id_]) for id_ in real_dict}
pred_dict = {id_: post_process_sql(pred_dict[id_]) for id_ in pred_dict}

current_real_dir = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(current_real_dir, 'mimic_iv.sqlite')
if not os.path.exists(db_path):
    raise Exception('File does not exist: %s' % db_path)

num_workers = mp.cpu_count()
if num_workers > 1:
    from scoring_utils import execute_all_distributed
    real_result = execute_all_distributed(real_dict, db_path, tag='real', num_workers=num_workers)
    pred_result = execute_all_distributed(pred_dict, db_path, tag='pred', num_workers=num_workers)
else:
    from scoring_utils import execute_all
    real_result = execute_all(real_dict, db_path, tag='real')
    pred_result = execute_all(pred_dict, db_path, tag='pred')


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