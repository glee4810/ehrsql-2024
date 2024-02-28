import os
import sys
import json
import sqlite3
import numpy as np
import multiprocessing as mp


def process_answer(ans):
    return str(sorted([str(ret) for ret in ans])[:100]) # check only up to 100th record

def execute_sql(sql, db_path):
    con = sqlite3.connect(db_path)
    con.text_factory = lambda b: b.decode(errors="ignore")
    cur = con.cursor()
    result = cur.execute(sql).fetchall()
    con.close()
    return process_answer(result)

def execute_sql_wrapper(key, sql, db_path, tag, skip_indicator='null'):
    assert tag in ['real', 'pred']
    if sql != skip_indicator:
        try:
            result = execute_sql(sql, db_path)
        except:
            result = 'error_'+tag
        return (key, result)
    else:
        return (key, skip_indicator)

def execute_all(dict, db_path, tag):
    exec_result = {}
    for key in dict:
        sql = dict[key]
        exec_result[key] = execute_sql_wrapper(key, sql, db_path, tag)[-1]
    return exec_result

def execute_all_distributed(dict, db_path, tag, num_workers):
    exec_result = {}
    def result_tracker(result):
        exec_result[result[0]] = result[-1]
    pool = mp.Pool(processes=num_workers)
    for key in dict:
        sql = dict[key]
        pool.apply_async(execute_sql_wrapper, args=(key, sql, db_path, tag), callback = result_tracker)
    pool.close()
    pool.join()
    return exec_result

def reliability_score(real_result, pred_result, return_dict=False):

    reliablity_score = []
    reliablity_score_dict = {}
    for key in real_result:
        ans_real = real_result[key]
        ans_pred = pred_result[key]
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
            NotImplementedError
        reliablity_score.append(score)
        reliablity_score_dict[key] = score

    if return_dict:
        return reliablity_score, reliablity_score_dict
    else:
        return reliablity_score

def penalize(scores, penalty=1):
    return np.mean([score*penalty if score == -1 else score for score in scores])