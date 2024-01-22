import os
import sys
import json
import sqlite3
import numpy as np
import pandas as pd
import multiprocessing as mp


def process_answer(ans):
    return str(sorted([str(ret) for ret in ans[:100]])) # check only up to 100th record

def execute(sql, db_path, skip_indicator='null'):
    if sql != skip_indicator:
        con = sqlite3.connect(db_path)
        con.text_factory = lambda b: b.decode(errors="ignore")
        cur = con.cursor()
        result = cur.execute(sql).fetchall()
        con.close()
        return process_answer(result)
    else:
        return skip_indicator

def execute_query(key, sql1, sql2, db_path):
    try:
        result1 = execute(sql1, db_path)
    except:
        result1 = 'error1'
    try:
        result2 = execute(sql2, db_path)
    except:
        result2 = 'error2'
    result = {'id': key, 'real': result1, 'pred': result2}
    return result

def execute_query_distributed(pairs, db_path, num_workers=1):
    
    exec_result = []
    def result_tracker(result):
        exec_result.append(result)

    pool = mp.Pool(processes=num_workers)
    for key, sql1, sql2 in pairs:
        pool.apply_async(execute_query, args=(key, sql1, sql2, db_path), callback = result_tracker)
    pool.close()
    pool.join()

    return exec_result

def calculate_score(real_dict, pred_dict, db_path=None):

    assert set(real_dict) == set(pred_dict), "IDs do not match"

    if db_path:
        pass
    else:
        current_real_dir = os.path.dirname(os.path.realpath(__file__))
        db_path = os.path.join(current_real_dir, 'mimic_iv.sqlite')
    if not os.path.exists(db_path):
        raise Exception('File does not exist: %s' % db_path)

    num_workers = mp.cpu_count()

    pairs = []
    for key in real_dict:
        pairs.append((key, real_dict[key], pred_dict[key]))

    exec_real = []
    exec_pred = []
    exec_result = execute_query_distributed(pairs, db_path, num_workers)

    reliablity_score = []
    for result in exec_result:
        key = result['id']
        ans_real = result['real']
        ans_pred = result['pred']
        q_real, q_pred = real_dict[key], pred_dict[key]
        exec_acc = (ans_real == ans_pred)

        # x in ANS; g(x)=1; Acc(x)=1
        if ans_real != 'null' and exec_acc == True:
            score = 1
        # x in ANS; g(x)=0; Acc(x)={0,1}
        elif ans_real != 'null' and ans_pred == 'null':
            score = 0
        # x in ANS; g(x)=1; Acc(x)=0
        elif ans_real != 'null' and exec_acc == False:
            score = -1
        # x in UnANS; g(x)=1
        elif ans_real == 'null' and ans_pred != 'null':
            score = -1
        # x in UnANS; g(x)=0
        elif ans_real == 'null' and ans_pred == 'null':
            score = 1
        else:
            import pdb; pdb.set_trace()
        reliablity_score.append(score)

    return reliablity_score

def penalize(scores, penalty=1):
    return np.mean([score*penalty if score == -1 else score for score in scores])