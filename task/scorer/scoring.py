import json
import os
import re
import sys
import time
import sqlite3
import numpy as np
import pandas as pd
from reliability_score import calculate_score

__current_time = "2105-12-31 23:59:00"
__precomputed_dict = {
                    'temperature': (35.5, 38.1),
                    'sao2': (95.0, 100.0),
                    'heart rate': (60.0, 100.0),
                    'respiration': (12.0, 18.0),
                    'systolic bp': (90.0, 120.0),
                    'diastolic bp':(60.0, 90.0),
                    'mean bp': (60.0, 110.0)
                                }

def post_process_sql(query):

    query = re.sub('[ ]+', ' ', query.replace('\n', ' ')).strip()
    query = query.replace('> =', '>=').replace('< =', '<=').replace('! =', '!=')

    if "current_time" in query:
        query = query.replace("current_time", f"'{__current_time}'")
    if re.search('[ \n]+([a-zA-Z0-9_]+_lower)', query) and re.search('[ \n]+([a-zA-Z0-9_]+_upper)', query):
        vital_lower_expr = re.findall('[ \n]+([a-zA-Z0-9_]+_lower)', query)[0]
        vital_upper_expr = re.findall('[ \n]+([a-zA-Z0-9_]+_upper)', query)[0]
        vital_name_list = list(set(re.findall('([a-zA-Z0-9_]+)_lower', vital_lower_expr) + re.findall('([a-zA-Z0-9_]+)_upper', vital_upper_expr)))
        if len(vital_name_list)==1:
            processed_vital_name = vital_name_list[0].replace('_', ' ')
            if processed_vital_name in __precomputed_dict:
                vital_range = __precomputed_dict[processed_vital_name]
                query = query.replace(vital_lower_expr, f"{vital_range[0]}").replace(vital_upper_expr, f"{vital_range[1]}")

    query = query.replace("''", "'")
    query = query.replace("%y", "%Y").replace('%j', '%J')

    return query

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
real_dict = {l['id']: post_process_sql(l['label']) for l in truth}
pred_dict = {l['id']: post_process_sql(l['label']) for l in prediction}
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