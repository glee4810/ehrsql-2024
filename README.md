# Reliable Text-to-SQL on Electronic Health Records - Clinical NLP Workshop @ NAACL 2024

<p align="left" float="left">
  <img src="image/logo.png" height="100" />
</p>


This task is part of the shared tasks at [NAACL 2024 - Clinical NLP](https://clinical-nlp.github.io/2024) and is launched on the Codabench platform: [https://www.codabench.org/competitions/1889](https://www.codabench.org/competitions/1889).

Electronic Health Records (EHRs) are relational databases that store a patient’s entire medical history in the hospital. From hospital admission to patient treatment and discharge, EHRs record and store various medical events that occur during a patient's hospital stay. While they are invaluable sources of clinical knowledge, exploring them beyond a pre-defined set of queries requires proficiency in query languages such as SQL. An alternative approach is to build a text-to-SQL system that can automatically translate natural language questions directly into the corresponding SQL queries.

The goal of this task is to develop a reliable text-to-SQL system for EHRs. Unlike standard text-to-SQL tasks, this task focuses on building reliable systems that are capable of handling diverse input questions, including both answerable and unanswerable ones within the context of the EHR database schema. For answerable questions, the system must accurately generate SQL queries while avoiding incorrect predictions. When it comes to unanswerable questions, the system must correctly identify them as such to prevent the generation of SQL queries for infeasible questions. The range of questions encompasses patient demographics, vital signs, specific disease survival rates, and more ([EHRSQL](https://github.com/glee4810/EHRSQL)). Unanswerable questions consist of two types: (1) real-world questions collected in a hospital (from EHRSQL) that happen to go beyond the EHR database schema (MIMIC-IV) and (2) hidden questions adversarially crafted to deceive text-to-SQL models. Successfully solving this task will lead to the development of a reliable question-answering system for EHRs, which will significantly alleviate the burden of knowledge retrieval in hospitals.



[Timeline](#timeline) | [Dataset](#dataset) | [Evaluation Metric](#scorer_and_official_evaluation_metric) | [Baselines](#baselines) | [Submission](#submission) | [Communication and Contact](#communication_and_contacts) | [Organizers](#organizers)



## <a name="timeline"></a>Timeline

* Registration opens: Monday January 29, 2024
* Training and validation data release: Monday January 29, 2024
* Test data release: Monday February 26, 2024
* Run submission due: Friday March 1, 2024
* Code submission and fact sheet deadline: Monday March 4, 2024
* Final result release: Monday March 11, 2024
* Paper submission due: Tuesday March 19, 2024
* Notification of acceptance: Tuesday April 16, 2024
* Final versions of papers due: Wednesday April 24, 2024
* Clinical NLP Workshop @ NAACL 2024: June 21 or 22, 2024, Mexico City, Mexico


## <a name="dataset"></a>Dataset

<!-- ### Statistics
| #Train | #Valid | #Test |
|:-------:|:-------:|:-------:|
| 9680 (TBD) | 1260 (TBD) | 1698 (TBD) | -->


### Data Relase

- The training and validation data will be released on January 29, 2024.
- The test data will be released on February 26, 2024.


### Data Format

For the task, we have two types of files for each of the training, validation, and test sets: data files (with names like \*_data.json) and label files (with names like \*_label.json). Data files contain the input data for the model, and label files contain the expected model outputs that share the same 'id's as the corresponding data files.

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



#### Table Schema

We follow the same table information style used in [Spider](https://github.com/taoyds/spider). `tables.json` contains the following information for both databases:

- `db_id`: the ID of the database
- `table_names_original`: the original table names stored in the database.
- `table_names`: the cleaned and normalized table names.
- `column_names_original`: the original column names stored in the database. Each column has the format `[0, "id"]`. `0` is the index of the table name in `table_names`. `"id"` is the column name. 
- `column_names`: the cleaned and normalized column names.
- `column_types`: the data type of each column
- `foreign_keys`: the foreign keys in the database. `[7, 2]` indicates the column indices in `column_names`. that correspond to foreign keys in two different tables.
- `primary_keys`: the primary keys in the database. Each number represents the index of `column_names`.


```json
{
    "column_names": [
      [
        -1,
        "*"
      ],      
      [
        0,
        "row id"
      ],
      [
        0,
        "subject id"
      ],
      [
        0,
        "gender"
      ],
      [
        0,
        "dob"
      ],
      ...
    ],
    "column_names_original": [
      [
        -1,
        "*"
      ],      
      [
        0,
        "row_id"
      ],
      [
        0,
        "subject_id"
      ],
      [
        0,
        "gender"
      ],
      [
        0,
        "dob"
      ],
      ...
    ],
    "column_types": [
      "text",
      "number",
      "number",
      "text",
      "time",
      ...
    ],
    "db_id": "mimic_iv",
    "foreign_keys": [
      [
        7,
        2
      ],
      ...
    ],
    "primary_keys": [
      1,
      6,
      ...
    ],
    "table_names": [
      "patients",
      "admissions",
      ...
    ],
    "table_names_original": [
      "patients",
      "admissions",
      ...
    ]
  }
```


#### Database

We use the [MIMIC-IV database demo](https://physionet.org/content/mimic-iv-demo/2.2/), which anyone can access the files as long as they conform to the terms of the [Open Data Commons Open Database License v1.0](https://physionet.org/content/mimic-iv-demo/view-license/2.2/). If you agree to the terms, use the bash command below to download the database.

```
wget https://physionet.org/static/published-projects/mimic-iv-demo/mimic-iv-clinical-database-demo-2.2.zip
unzip mimic-iv-clinical-database-demo-2.2
gunzip -r mimic-iv-clinical-database-demo-2.2
```


Once downloaded, run the code below to preprocess the database. This step involves time-shifting, value deduplication in tables, and more.

```
cd preprocess
bash preprocess.sh
cd ..
```



## <a name="scorer_and_official_evaluation_metric"></a>Evaluation Metric

The scorer for the task is located in the scorer module. The scorer (scoring.py) will report the official evaluation score. More details about the metric in the [Evaluation](https://www.codabench.org/competitions/1889) tab on the task website.



## <a name="baselines"></a>Baseline


We provide three sample baseline code examples on Colab as starters.

### ["Dummy" Model Sample Code](https://colab.research.google.com/drive/1ZRhWr_o6-vyc0FKGAf1nuGZVycqyy-p-?usp=sharing)

Generates 'null' for all predictions. This will mark all questions as unanswerable, and the reliability scores will match the percentage of unanswerable questions in the evaluation set.

### [Local Model Sample Code (T5)](https://colab.research.google.com/drive/1MmwWGcCIZ_B8ZQk761pehId1T7CYs5D1?usp=sharing)

Generates predictions using T5.

### [OpenAI Model Sample Code (ChatGPT)](https://colab.research.google.com/drive/1OpmRjbHXO7u8_6_meCy_g-ukqSlZDanQ?usp=sharing)

Generates predictions using ChatGPT. 



## <a name="submission"></a>Submission

### File Format

After saving your prediction file, compress (zip) it using a bash command, for example:
```
zip predictions.zip prediction.json
```

### Submitting the File

Submit your prediction file on our task website on Codabench. For more details, see the [Submission](https://www.codabench.org/competitions/1889) tab.



## <a name="contacts"></a>Contacts

For general communications: Please, use our Google group at [https://groups.google.com/g/ehrsql-2024/](https://groups.google.com/g/ehrsql-2024/). Important announcements and discussions are posted and discussed in our Google group.



## <a name="organizers"></a>Organizers

Organizers are from [EdLab](https://mp2893.com/) @ [KAIST AI](https://gsai.kaist.ac.kr/).

- Edward Choi
- Gyubok Lee
- Sunjun Kweon
- Seongsu Bae
