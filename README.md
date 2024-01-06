# Reliable Text-to-SQL on Electronic Health Records @ NAACL - Clinical NLP 2024

<p align="left" float="left">
  <img src="image/logo.png" height="100" />
</p>


[Competition](#competition) | [Timeline](#timeline) | [Data Format](#data_format) | [Evaluation Metric](#scorer_and_official_evaluation_metric) | [Baselines](#baselines) | [Submission](#submission) | [Organizers](#organizers) | [Contacts](#contacts)


Electronic Health Records (EHRs) are relational databases that store a patient’s entire medical history in the hospital. From hospital admission to patient treatment and discharge, EHRs record and store various medical events that occur during a patient's hospital stay. While they are invaluable sources of clinical knowledge, exploring them beyond a pre-defined set of queries requires proficiency in query languages such as SQL. An alternative approach is to build a text-to-SQL system that can automatically translate natural language questions directly into the corresponding SQL queries.

The goal of the task is to develop a reliable text-to-SQL system on EHRs. Unlike standard text-to-SQL tasks, this system must handle all types of questions, including answerable and unanswerable ones with respect to the EHR database structure. For answerable questions, the system must accurately generate SQL queries. For unanswerable questions, the system must correctly identify them as such, thereby preventing incorrect SQL predictions for infeasible questions. The range of questions includes answerable queries about MIMIC-IV, covering topics such as patient demographics, vital signs, and specific disease survival rates ([EHRSQL](https://github.com/glee4810/EHRSQL)). Additionally, there are specially designed unanswerable questions intended to challenge the system. Successfully completing this task will result in the creation of a reliable question-answering system for EHRs, significantly improving the flexibility and efficiency of clinical knowledge exploration in hospitals.



## <a name="competition"></a>Competition

Our competition is launched on the CodaBench platform: [https://www.codabench.org/competitions/1889](https://www.codabench.org/competitions/1889).


## <a name="timeline"></a>Timeline

* Registration opens: Jan 29 (Mon), 2024
* Training & dev data release: Jan 29 (Mon), 2024
* Test data release: Feb 26 (Mon), 2024
* Test submission deadline: Mar 1 (Fri), 2024
* Code submission and fact sheet deadline: Mar 4 (Mon), 2024
* Final result release (ones that are code-verified): Mar 11 (Mon), 2024
* Paper Deadline: Mar 21 (Wed), 2024
* Notification of acceptance: Apr 19 (Fri), 2023
* Camera-ready system papers due: May 2 (Thu), 2024
* Clinical NLP Workshop Date: June 20 (Thu) or 21 (Fri), 2024


## <a name="data_format"></a>Data Format

### Statistics
| #Train | #Dev | #Test |
|:-------:|:-------:|:-------:|
| 9680 (TBD) | 1260 (TBD) | 1698 (TBD) |


### Data Relase

- The training and dev data will be released on Jan 29, 2024.
- The test data will be released on Feb 26, 2024.


### Data Format

For the task, we have two types of files for each of the train, dev, and test sets: data files (with names like \*_data.json) and label files (with names like \*_label.json). Data files contain the input data for the model, and label files contain the expected model outputs that share the same 'id's as the corresponding data files.
#### Input Data (\*_data.json)
A list of python dictionary in the JSON format:
```
{
  id -> Identifier of the example,
  question -> Input question (This can be either answerable or unanswerable given the MIMIC-IV schema)
}
```

#### Output Data (\*_label.json)
A list of python dictionary in the JSON format:
```
{
  id -> Identifier of the example,
  label -> Label (SQL query or 'null')
}
```



## <a name="scorer_and_official_evaluation_metric"></a>Evaluation Metric

The scorer for the task is located in the scorer module. The scorer (scoring.py) will report the official evaluation metric. More details are in the [Task Desciption](https://www.codabench.org/competitions/1889) tab.




## <a name="baselines"></a>Baseline

### Option 1: Local-Model Sample Submission

TBD


### Option 2: OpenAI Model Sample Submission

TBD




## <a name="submission"></a>Submission

### File Format and Format Checker

A prediction file must be one single JSON file for all texts. The entry for each text must include the fields "id" and "label", same as \*_label.json.
The format checkers verify that your prediction file complies with the expected format. They are located in the ```format_checker``` module.
```python
python3 format_checker/format_checker.py --pred_files_path=<path_to_your_results_files> 
```

After checking the format, compress (zip) the prediction file, for example with a bash command:
```
zip predictions.zip prediction.json
```

### Submitting the File

Submit your prediction file on our task website on CodaBench. For more details, see the [Submission](https://www.codabench.org/competitions/1889) tab.




## <a name="organizers"></a>Organizers

Organizers are from [EdLab](https://mp2893.com/) @ [KAIST AI](https://gsai.kaist.ac.kr/).

- Edward Choi
- Gyubok Lee
- Sunjun Kweon
- Seongsu Bae


## <a name="contacts"></a>Contacts

Google group: [https://groups.google.com/g/ehrsql/](https://https://groups.google.com/g/ehrsql-2024/)  
Email: ehrsql-2024@googlegroups.com