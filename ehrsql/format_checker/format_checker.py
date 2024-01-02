import os
import argparse
import logging
import json
import pandas as pd
"""
This script checks whether the results format. 
It also provides some warnings about possible errors.

The submission of the result file should be in json format.
It should be a list of lines of objects:
[
    {
        id    -> identifier of the sample,
        label -> label (sql prediction or 'null'),
    },
    ...
]
"""

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
COLUMNS = ['id', 'label']


def check_format(file_path):
  if not os.path.exists(file_path):
    logging.error("File doesnt exists: {}".format(file_path))
    return False
  
  try:
    with open(file_path) as f:
      submission_raw = json.load(f)
    prediction = []
    for line in submission_raw:
      for column in COLUMNS:
        if column not in line:
          return False
          break
        prediction.append(line['label'])
  except:
    logging.error("File is not a valid json file: {}".format(file_path))
    return False
  
  if prediction.count('null')>len(prediction)//2:
    logging.error("The 'null' is more than 50\% of the predictions")
    return False
  
  return True


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("--pred_files_path", "-p", nargs='+', required=True, 
    help="Path to the files you want to check.", type=str)

  args = parser.parse_args()
  logging.info("Checking files: {}".format(args.pred_files_path))
  
  for pred_file_path in args.pred_files_path:
    check_result = check_format(pred_file_path)
    result = 'Format is correct' if check_result else 'Something wrong in file format'
    logging.info("Checking file: {}. Result: {}".format(args.pred_files_path, result))


# python3 format_checker/format_checker.py --pred_files_path=<path_to_your_results_files>