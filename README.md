# Reliable Text-to-SQL on Electronic Health Records - Clinical NLP Workshop @ NAACL 2024


## [Overview](https://sites.google.com/view/ehrsql-2024)

Electronic Health Records (EHRs) are relational databases that store the entire medical histories of patients within hospitals. They record numerous aspects of a patient's medical care, from admission and diagnosis to treatment and discharge. While EHRs are vital sources of clinical data, exploring them beyond a predefined set of queries requires skills in query languages like SQL. To make this process more accessible, one could develop a text-to-SQL system that automatically translates natural language questions into corresponding SQL queries. In this task, we aim to develop a reliable text-to-SQL system specifically tailored for EHRs.

This is part of the shared tasks at [NAACL 2024 - Clinical NLP](https://clinical-nlp.github.io/2024).

- Task overview: [https://sites.google.com/view/ehrsql-2024](https://sites.google.com/view/ehrsql-2024)
- Task platform: [https://www.codabench.org/competitions/1889](https://www.codabench.org/competitions/1889)
- Dataset: [https://github.com/glee4810/ehrsql-2024](https://github.com/glee4810/ehrsql-2024)


<p align="left" float="left">
  <img src="image/logo.png" height="100" />
</p>

[Timeline](#timeline) | [Dataset](#dataset) | [Evaluation](#evaluation) | [Baselines](#baselines) | [Submission](#submission) | [Contact](#contact) | [Organizer](#organizer)



## <a name="timeline"></a>Timeline

All deadlines are 11:59PM UTC-12:00 ([Anywhere on Earth](https://www.timeanddate.com/time/zones/aoe)), unless stated otherwise

* ~~Registration opens: Monday January 29, 2024~~
* ~~Training and validation data release: Monday January 29, 2024~~
* ~~Test data release: Tuesday March 26, 2024~~
* ~~Run submission due: Thursday March 28, 2024 (11:59PM UTC)~~
* ~~Code submission and fact sheet deadline: Friday March 29, 2024~~
* ~~Final result release: Monday April 1, 2024~~
* Paper submission period starts: Monday April 8, 2024
* Paper submission due: Wednesday April 10, 2024
* Notification of acceptance: Thursday April 18, 2024
* Final versions of papers due: Wednesday April 24, 2024
* Clinical NLP Workshop @ NAACL 2024: June 21 or 22, 2024, Mexico City, Mexico


## <a name="dataset"></a>Dataset

### Statistics
| #Train | #Valid | #Test |
|:-------:|:-------:|:-------:|
| 5124 | 1163 | 1167 |


### Data Format

For the task, we have two types of files for each of the train, dev, and test sets: data files (with names like \*_data.json) and label files (with names like \*_label.json). Data files contain the input data for the model, and label files contain the expected model outputs that share the same 'id's as the corresponding data files ([sample data](https://github.com/glee4810/ehrsql-2024/tree/master/sample_data/train)).


#### Input Data (data.json)

```
{
  "version" : dataset version,
	"data" : [
	  {
		  "id" : sample identifier,
			"question" : natural langauge question (either answerable or unanswerable given the MIMIC-IV schema),	
	  },
	...		
	]
}
```

Each object in the data list consists of an ID and the corresponding natural language question.


#### Output Data (label.json)

```
{
  id -> sample identifier : label -> SQL query or 'null' if subject to abstention,
	...
}
```

Each object has a key of a sample's ID and a value of the corresponding label.



##### Table Schema

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
      ...
    ],
    "column_types": [
      "text",
      "number",
      "number",
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


### Database

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



## <a name="evaluation"></a>Evaluation

The scorer (`scoring.py` in the scoring_program module) will report the official evaluation score for the task. For more details about the metric, please refer to the [Evaluation](https://www.codabench.org/competitions/1889) tab on the Codabench website.



## <a name="baselines"></a>Baseline


We provide three sample baseline code examples on Colab as starters.

### ["Dummy" Model Sample Code](https://colab.research.google.com/drive/1ZRhWr_o6-vyc0FKGAf1nuGZVycqyy-p-?usp=sharing)

Generates 'null' for all predictions. This will mark all questions as unanswerable, and the reliability scores will match the percentage of unanswerable questions in the evaluation set.

### [Local Model Sample Code (T5)](https://colab.research.google.com/drive/1MmwWGcCIZ_B8ZQk761pehId1T7CYs5D1?usp=sharing)

Generates predictions using T5.

### [OpenAI Model Sample Code (ChatGPT)](https://colab.research.google.com/drive/1OpmRjbHXO7u8_6_meCy_g-ukqSlZDanQ?usp=sharing)

Generates predictions using ChatGPT. 



## <a name="submission"></a>Submission

#### File Format

After saving your prediction file, compress (zip) it using a bash command, for example:
```
zip predictions.zip prediction.json
```


#### Submitting the File

Submit your prediction file on our task website on Codabench. For more details, see the [Submission](https://www.codabench.org/competitions/1889) tab.



## <a name="contact"></a>Contact

For more updates, join our Google group [https://groups.google.com/g/ehrsql-2024/](https://groups.google.com/g/ehrsql-2024/).



## <a name="organizer"></a>Organizer

Organizers are from [EdLab](https://mp2893.com/) @ [KAIST](https://gsai.kaist.ac.kr/).

* [Edward Choi](https://mp2893.com/)
* [Gyubok Lee](https://sites.google.com/view/gyuboklee)
* Sunjun Kweon
* [Seongsu Bae](https://seongsubae.info/)

