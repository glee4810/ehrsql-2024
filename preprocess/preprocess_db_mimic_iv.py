import os
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random
from ast import literal_eval
import pandas as pd
import numpy as np
from collections import Counter
import sqlite3

import warnings

warnings.filterwarnings("ignore")

from preprocess_utils import Sampler, adjust_time, read_csv, generate_random_date


CHARTEVENT2ITEMID = {
    "Temperature Celsius": "223762",  # body temperature
    "O2 saturation pulseoxymetry": "220277",  # Sao2
    "Heart Rate": "220045",  # heart rate
    "Respiratory Rate": "220210",  # respiration rate
    "Arterial Blood Pressure systolic": "220050",  # systolic blood pressure
    "Arterial Blood Pressure diastolic": "220051",  # diasolic blood pressure
    "Arterial Blood Pressure mean": "220052",  # mean blood pressure
    # "Admission Weight (Kg)": "226512",  # weight
    "Daily Weight": "224639",  # majority labels for weight but not used in MIMIC-IV (followed by MIMIC-III)
    "Height (cm)": "226730",  # height
}

# value duplication in other tables
_remove_from_diagnosis = ['artificial insemination', 'dental examination', 'insertion of intrauterine contraceptive device']

# Disambiguate values in the fields d_item.label, d_labitems.label, and prescription.drug, keeping only the most frequent label.
_keep_label = {'micafungin': 'inputevents', 'propofol': 'inputevents', 'progesterone': 'prescriptions', 'lr': 'inputevents', 'ambisome': 'inputevents', 'ceftaroline': 'inputevents', 'epinephrine': 'inputevents', 'magnesium sulfate': 'inputevents', 'albumin 25%': 'inputevents', 'caspofungin': 'inputevents', 'nan': 'prescriptions', 'ciprofloxacin': 'inputevents', 'atropine': 'inputevents', 'fentanyl': 'inputevents', 'dextrose 50%': 'inputevents', 'atovaquone': 'inputevents', 'penicillin g potassium': 'inputevents', 'heparin': 'prescriptions', 'diltiazem': 'inputevents', 'dilantin': 'inputevents', 'esmolol': 'inputevents', 'testosterone': 'labevents', 'dopamine': 'inputevents', 'potassium phosphate': 'inputevents', 'albumin': 'labevents', 'ensure': 'inputevents', 'verapamil': 'inputevents', 'procainamide': 'prescriptions', 'ceftriaxone': 'inputevents', 'ceftazidime': 'inputevents', 'd5ns': 'inputevents', 'citrate': 'inputevents', 'tobramycin': 'labevents', 'solution': 'inputevents', 'phenylephrine': 'inputevents', 'primidone': 'prescriptions', 'vasopressin': 'inputevents', 'doxycycline': 'inputevents', 'albumin 5%': 'inputevents', 'ribavirin': 'inputevents', 'metronidazole': 'inputevents', 'multivitamins': 'inputevents', 'potassium': 'prescriptions', 'tamiflu': 'inputevents', 'factor xiii': 'labevents', 'meropenem': 'inputevents', 'oxycodone': 'labevents', 'protamine sulfate': 'inputevents', 'd5 1/2ns': 'inputevents', 'rocuronium': 'inputevents', 'calcium chloride': 'inputevents', 'test': 'prescriptions', 'phenobarbital': 'prescriptions', 'calcium gluconate': 'inputevents', 'linezolid': 'inputevents', 'potassium chloride': 'inputevents', 'clindamycin': 'inputevents', 'adenosine': 'inputevents', 'morphine sulfate': 'inputevents', 'chloroquine': 'inputevents', 'folic acid': 'inputevents', 'amikacin': 'prescriptions', 'nafcillin': 'inputevents', 'daptomycin': 'inputevents', 'd5lr': 'inputevents', 'sodium': 'labevents', 'quinidine': 'prescriptions', 'moxifloxacin': 'inputevents', 'mannitol': 'inputevents', 'ampicillin': 'inputevents', 'isoniazid': 'inputevents', 'fluconazole': 'inputevents', 'lithium': 'labevents', 'keflex': 'inputevents', 'folate': 'inputevents', 'colistin': 'inputevents', 'ranitidine': 'inputevents', 'argatroban': 'inputevents', 'dobutamine': 'inputevents', 'cisatracurium': 'inputevents', 'dextrose 5%': 'inputevents', 'levofloxacin': 'inputevents', 'factor viii': 'inputevents', 'acetaminophen': 'prescriptions', 'd': 'prescriptions', 'lidocaine': 'prescriptions', 'theophylline': 'labevents', 'vancomycin': 'prescriptions', 'methotrexate': 'prescriptions', 'aminophylline': 'inputevents', 'hydrochloric acid': 'inputevents', 'nesiritide': 'inputevents', 'hydromorphone (dilaudid)': 'inputevents', 'octreotide': 'inputevents', 'gentamicin': 'prescriptions', 'nicardipine': 'inputevents', 'rifampin': 'inputevents', 'amiodarone': 'inputevents', 'tigecycline': 'inputevents', 'magnesium': 'labevents', 'insulin': 'prescriptions', 'hydralazine': 'inputevents', 'labetalol': 'inputevents', 'cyclosporine': 'inputevents', 'sodium bicarbonate 8.4%': 'inputevents', 'potassium acetate': 'inputevents', 'aztreonam': 'inputevents', 'cefepime': 'inputevents', 'carbamazepine': 'labevents', 'norepinephrine': 'inputevents', 'digoxin': 'prescriptions', 'milrinone': 'inputevents', 'heparin sodium': 'inputevents', 'valproic acid': 'labevents', 'foscarnet': 'inputevents', 'mannitol 20%': 'inputevents', 'd5 1/4ns': 'inputevents', 'phenytoin': 'labevents', 'iron': 'labevents', 'acetylcysteine': 'inputevents', 'epoprostenol (veletri)': 'inputevents', 'pyrazinamide': 'inputevents', 'sodium acetate': 'inputevents', 'acyclovir': 'inputevents', 'oxacillin': 'inputevents', 'ketamine': 'inputevents', 'fosphenytoin': 'inputevents', 'sterile water': 'inputevents', 'metoprolol': 'inputevents', 'nitroglycerin': 'inputevents', 'erythromycin': 'inputevents', 'estradiol': 'labevents', 'voriconazole': 'inputevents', 'pamidronate': 'inputevents', 'cefazolin': 'inputevents', 'azithromycin': 'inputevents', 'fondaparinux': 'inputevents', 'lepirudin': 'inputevents', 'thiamine': 'inputevents', 'thrombin': 'labevents', 'zinc': 'prescriptions'}


class Build_MIMIC_IV(Sampler):
    def __init__(
        self,
        data_dir,
        out_dir,
        db_name,
        num_patient,
        sample_icu_patient_only,
        deid=False,
        timeshift=False,
        cur_patient_ratio=0.0,
        start_year=None,
        time_span=None,
        current_time=None,
        verbose=True,
    ):
        super().__init__()

        self.data_dir = data_dir
        self.out_dir = os.path.join(out_dir, db_name)

        self.deid = deid
        self.timeshift = timeshift

        self.sample_icu_patient_only = sample_icu_patient_only
        self.num_patient = num_patient
        self.num_cur_patient = int(self.num_patient * cur_patient_ratio)
        self.num_non_cur_patient = self.num_patient - int(self.num_patient * cur_patient_ratio)

        if self.timeshift:
            self.start_year = start_year
            self.start_pivot_datetime = datetime(year=self.start_year, month=1, day=1)
            self.time_span = time_span
            self.current_time = current_time
            if verbose:
                print("timeshift is True")
                print(f"start_year: {self.start_year}")
                print(f"time_span: {self.time_span}")
                print(f"current_time: {self.current_time}")

        self.conn = sqlite3.connect(os.path.join(self.out_dir, db_name + ".sqlite"))
        self.cur = self.conn.cursor()
        with open(os.path.join(self.out_dir, db_name + ".sql"), "r") as sql_file:
            sql_script = sql_file.read()
        self.cur.executescript(sql_script)

        self.chartevent2itemid = {k.lower(): v for k, v in CHARTEVENT2ITEMID.items()}  # lower case

    def build_admission_table(self):
        print("Processing patients, admissions, icustays, transfers")
        start_time = time.time()

        # read patients
        PATIENTS_table = read_csv(
            self.data_dir,
            "hosp/patients.csv",
            columns=["subject_id", "gender", "anchor_age", "anchor_year", "dod"],
            lower=True,
        )
        PATIENTS_table = PATIENTS_table.reset_index().rename(columns={"index": "row_id"})

        subjectid2anchor_year = {pid: anch_year for pid, anch_year in zip(PATIENTS_table["subject_id"].values, PATIENTS_table["anchor_year"].values)}
        subjectid2anchor_age = {pid: anch_age for pid, anch_age in zip(PATIENTS_table["subject_id"].values, PATIENTS_table["anchor_age"].values)}

        # add new column `dob` and remove anchor columns
        PATIENTS_table = PATIENTS_table.assign(dob=lambda x: x["anchor_year"] - x["anchor_age"])
        PATIENTS_table = PATIENTS_table[["row_id", "subject_id", "gender", "dob", "dod"]]
        # NOTE: the month and day of dob are randomly sampled
        PATIENTS_table["dob"] = PATIENTS_table["dob"].apply(lambda x: generate_random_date(x))
        # NOTE: time format (dob/dod)
        for col in ["dob", "dod"]:
            PATIENTS_table[col] = pd.to_datetime(PATIENTS_table[col], format="%Y-%m-%d")
            PATIENTS_table[col] = PATIENTS_table[col].dt.strftime(date_format="%Y-%m-%d 00:00:00")

        # read admissions
        ADMISSIONS_table = read_csv(
            self.data_dir,
            "hosp/admissions.csv",
            columns=[
                "subject_id",
                "hadm_id",
                "admittime",
                "dischtime",
                "admission_type",
                "admission_location",
                "discharge_location",
                "insurance",
                "language",
                "marital_status",
                # "ethnicity",  # TODO: check if this column is needed
            ],
            lower=True,
        )
        ADMISSIONS_table = ADMISSIONS_table.reset_index().rename(columns={"index": "row_id"})

        # compute admission age
        ADMISSIONS_table["age"] = [
            int((datetime.strptime(admtime, "%Y-%m-%d %H:%M:%S")).year) - subjectid2anchor_year[pid] + subjectid2anchor_age[pid]
            for pid, admtime in zip(ADMISSIONS_table["subject_id"].values, ADMISSIONS_table["admittime"].values)
        ]

        # remove age outliers
        # ADMISSIONS_table = ADMISSIONS_table[(ADMISSIONS_table["age"] > 10) & (ADMISSIONS_table["age"] < 90)]

        # remove hospital stay outlier
        # hosp_stay_dict = {
        #     hosp: (datetime.strptime(dischtime, "%Y-%m-%d %H:%M:%S") - datetime.strptime(admtime, "%Y-%m-%d %H:%M:%S")).days
        #     for hosp, admtime, dischtime in zip(ADMISSIONS_table["hadm_id"].values, ADMISSIONS_table["admittime"].values, ADMISSIONS_table["dischtime"].values)
        # }
        # threshold_offset = np.percentile(list(hosp_stay_dict.values()), q=99)  # remove greater than 99% (31 days) or 95% (14 days) (for MIMIC-IV)
        # print(f"99% of hospital stays are less than {threshold_offset} days")
        # ADMISSIONS_table = ADMISSIONS_table[ADMISSIONS_table["hadm_id"].isin([hosp for hosp in hosp_stay_dict if hosp_stay_dict[hosp] < threshold_offset])]

        # NOTE: save original admittime
        self.HADM_ID2admtime_dict = {hadm: admtime for hadm, admtime in zip(ADMISSIONS_table["hadm_id"].values, ADMISSIONS_table["admittime"].values)}
        self.HADM_ID2dischtime_dict = {hadm: dischtime for hadm, dischtime in zip(ADMISSIONS_table["hadm_id"].values, ADMISSIONS_table["dischtime"].values)}

        # read icustays
        ICUSTAYS_table = read_csv(
            self.data_dir,
            "icu/icustays.csv",
            columns=["subject_id", "hadm_id", "stay_id", "first_careunit", "last_careunit", "intime", "outtime"],
            lower=True,
        )
        ICUSTAYS_table = ICUSTAYS_table.reset_index().rename(columns={"index": "row_id"})

        # subset only icu patients
        if self.sample_icu_patient_only:
            raise NotImplementedError("We do not support this option for MIMIC-IV yet.")
            # ADMISSIONS_table = ADMISSIONS_table[ADMISSIONS_table["subject_id"].isin(set(ICUSTAYS_table["subject_id"]))]

        # read transfer
        TRANSFERS_table = read_csv(
            self.data_dir,
            "hosp/transfers.csv",
            columns=["subject_id", "hadm_id", "transfer_id", "eventtype", "careunit", "intime", "outtime"],
            lower=True,
        )
        TRANSFERS_table = TRANSFERS_table.reset_index().rename(columns={"index": "row_id"})
        TRANSFERS_table = TRANSFERS_table.dropna(subset=["intime"])

        ################################################################################
        """
        Decide the offset (optimized for the MIMIC-IV + MIMIC-CXR)
        """
        if self.timeshift:
            # 1) get the earliest admission time of each patient, compute the offset, and save it
            ADMITTIME_earliest = {subj_id: min(ADMISSIONS_table["admittime"][ADMISSIONS_table["subject_id"] == subj_id].values) for subj_id in ADMISSIONS_table["subject_id"].unique()}
            self.subjectid2admittime_dict = {
                subj_id: self.first_admit_year_sampler(self.start_year, self.time_span, datetime.strptime(ADMITTIME_earliest[subj_id], "%Y-%m-%d %H:%M:%S").year)
                for subj_id in ADMISSIONS_table["subject_id"].unique()
            }

        ################################################################################
        """
        Since we start to adjust the time of the patients after this point,
        please do not change the offset (i.e., `self.subjectid2admittime_dict`)
        """
        # process patients
        if self.timeshift:
            PATIENTS_table["dob"] = adjust_time(PATIENTS_table, "dob", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            PATIENTS_table["dod"] = adjust_time(PATIENTS_table, "dod", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            PATIENTS_table = PATIENTS_table.dropna(subset=["dob"])

        # process admissions
        if self.timeshift:
            ADMISSIONS_table["admittime"] = adjust_time(
                ADMISSIONS_table,
                "admittime",
                # start_year=self.start_year,  # To avoid the admittime less than the start_year
                current_time=self.current_time,
                offset_dict=self.subjectid2admittime_dict,
                patient_col="subject_id",
            )
            ADMISSIONS_table["dischtime"] = adjust_time(
                ADMISSIONS_table,
                "dischtime",
                # start_year=self.start_year,  # To avoid the dischtime less than the start_year
                current_time=self.current_time,
                offset_dict=self.subjectid2admittime_dict,
                patient_col="subject_id",
            )
            ADMISSIONS_table = ADMISSIONS_table.dropna(subset=["admittime"])
            # flags = [] # ADDED
            # for id_, flag in zip(ADMISSIONS_table['subject_id'].values, ADMISSIONS_table['hospital_expire_flag'].values):
            #     if flag == 1 and PATIENTS_table['dod'][PATIENTS_table['subject_id']==id_].isnull().any():
            #         flags.append(0)
            #     else:
            #         flags.append(flag)
            # ADMISSIONS_table['hospital_expire_flag'] = flags

        # process icustays
        if self.timeshift:
            ICUSTAYS_table["intime"] = adjust_time(ICUSTAYS_table, "intime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            ICUSTAYS_table["outtime"] = adjust_time(ICUSTAYS_table, "outtime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            ICUSTAYS_table = ICUSTAYS_table.dropna(subset=["intime"])

        # process transfers
        if self.timeshift:
            TRANSFERS_table["intime"] = adjust_time(TRANSFERS_table, "intime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            TRANSFERS_table["outtime"] = adjust_time(TRANSFERS_table, "outtime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            TRANSFERS_table = TRANSFERS_table.dropna(subset=["intime"])

        ################################################################################
        """
        Decide the final cohort of patients: `self.cur_patient_list` and `self.non_cur_patient`
        """
        # sample current patients
        try:
            self.cur_patient_list = self.rng.choice(
                ADMISSIONS_table["subject_id"][ADMISSIONS_table["dischtime"].isnull()].unique(),
                self.num_cur_patient,
                replace=False,
            ).tolist()
        except:
            print("Cannot take a larger sample than population when 'replace=False")
            print("Use all available patients instead.")
            self.cur_patient_list = ADMISSIONS_table["subject_id"][ADMISSIONS_table["dischtime"].isnull()].unique().tolist()

        # sample non-current patients
        try:
            self.non_cur_patient = self.rng.choice(
                ADMISSIONS_table["subject_id"][(ADMISSIONS_table["dischtime"].notnull()) & (~ADMISSIONS_table["subject_id"].isin(self.cur_patient_list))].unique(),
                self.num_non_cur_patient,
                replace=False,
            ).tolist()
        except:
            print("Cannot take a larger sample than population when 'replace=False")
            print("Use all available patients instead.")
            self.non_cur_patient = ADMISSIONS_table["subject_id"][(ADMISSIONS_table["dischtime"].notnull()) & (~ADMISSIONS_table["subject_id"].isin(self.cur_patient_list))].unique().tolist()

        self.patient_list = self.cur_patient_list + self.non_cur_patient
        print(f"num_cur_patient: {len(self.cur_patient_list)}")
        print(f"num_non_cur_patient: {len(self.non_cur_patient)}")
        print(f"num_patient: {len(self.patient_list)}")

        PATIENTS_table = PATIENTS_table[PATIENTS_table["subject_id"].isin(self.patient_list)]
        ADMISSIONS_table = ADMISSIONS_table[ADMISSIONS_table["subject_id"].isin(self.patient_list)]

        self.hadm_list = list(set(ADMISSIONS_table["hadm_id"]))
        ICUSTAYS_table = ICUSTAYS_table[ICUSTAYS_table["hadm_id"].isin(self.hadm_list)]
        TRANSFERS_table = TRANSFERS_table[TRANSFERS_table["hadm_id"].isin(self.hadm_list)]

        if self.deid:  # de-identification
            rng_val = np.random.default_rng(0)  # init random generator
            random_indices = rng_val.choice(len(ICUSTAYS_table), len(ICUSTAYS_table), replace=False)

            careunit_mapping = {original: shuffled for original, shuffled in zip(ICUSTAYS_table["first_careunit"], ICUSTAYS_table["first_careunit"].iloc[random_indices])}
            careunit_mapping.update({original: shuffled for original, shuffled in zip(ICUSTAYS_table["last_careunit"], ICUSTAYS_table["last_careunit"].iloc[random_indices])})

            # shuffle ICUStays_table
            ICUSTAYS_table["first_careunit"] = ICUSTAYS_table["first_careunit"].map(careunit_mapping)
            ICUSTAYS_table["last_careunit"] = ICUSTAYS_table["last_careunit"].map(careunit_mapping)

            # shuffle TRANSFERS_table
            TRANSFERS_table["careunit"] = TRANSFERS_table["careunit"].replace(careunit_mapping)

        PATIENTS_table["row_id"] = range(len(PATIENTS_table))
        ADMISSIONS_table["row_id"] = range(len(ADMISSIONS_table))
        ICUSTAYS_table["row_id"] = range(len(ICUSTAYS_table))
        TRANSFERS_table["row_id"] = range(len(TRANSFERS_table))

        PATIENTS_table.to_csv(os.path.join(self.out_dir, "patients.csv"), index=False)
        ADMISSIONS_table.to_csv(os.path.join(self.out_dir, "admissions.csv"), index=False)
        ICUSTAYS_table.to_csv(os.path.join(self.out_dir, "icustays.csv"), index=False)
        TRANSFERS_table.to_csv(os.path.join(self.out_dir, "transfers.csv"), index=False)

        print(f"patients, admissions, icustays, transfers processed (took {round(time.time() - start_time, 4)} secs)")

    def build_dictionary_table(self):
        print("Processing dictionary tables (d_icd_diagnoses, d_icd_procedures, d_labitems, d_items)")
        start_time = time.time()

        """
        d_icd_diagnoses
        """
        # read csv
        D_ICD_DIAGNOSES_table = read_csv(
            data_dir=self.data_dir,
            filename="hosp/d_icd_diagnoses.csv",
            columns=["icd_code", "icd_version", "long_title"],
            lower=True,
        )
        D_ICD_DIAGNOSES_table = D_ICD_DIAGNOSES_table[~D_ICD_DIAGNOSES_table['long_title'].isin(_remove_from_diagnosis)] # duplication in d_icd_procedures
        D_ICD_DIAGNOSES_table = D_ICD_DIAGNOSES_table.astype({"icd_code": str})
        D_ICD_DIAGNOSES_table['icd_code'] = [f'icd{v}|{c}' for v, c in zip(D_ICD_DIAGNOSES_table['icd_version'].values, D_ICD_DIAGNOSES_table['icd_code'].values)]
        D_ICD_DIAGNOSES_table = D_ICD_DIAGNOSES_table.drop(columns=["icd_version"])

        # preprocess
        D_ICD_DIAGNOSES_table = D_ICD_DIAGNOSES_table.dropna()
        D_ICD_DIAGNOSES_table = D_ICD_DIAGNOSES_table.drop_duplicates(subset=["icd_code"])  # NOTE: some icd codes have multiple long titles
        D_ICD_DIAGNOSES_table = D_ICD_DIAGNOSES_table.drop_duplicates(subset=["long_title"])  # NOTE: some long titles have multiple icd codes

        # save csv
        D_ICD_DIAGNOSES_table = D_ICD_DIAGNOSES_table.reset_index(drop=False)
        D_ICD_DIAGNOSES_table = D_ICD_DIAGNOSES_table.rename(columns={"index": "row_id"})  # add row_id
        D_ICD_DIAGNOSES_table["row_id"] = range(len(D_ICD_DIAGNOSES_table))
        D_ICD_DIAGNOSES_table.to_csv(os.path.join(self.out_dir, "d_icd_diagnoses.csv"), index=False)
        self.D_ICD_DIAGNOSES_dict = {item: val for item, val in zip(D_ICD_DIAGNOSES_table["icd_code"].values, D_ICD_DIAGNOSES_table["long_title"].values)}

        """
        d_icd_procedures
        """
        # read csv
        D_ICD_PROCEDURES_table = read_csv(
            data_dir=self.data_dir,
            filename="hosp/d_icd_procedures.csv",
            columns=["icd_code", "icd_version", "long_title"],
            lower=True,
        )
        D_ICD_PROCEDURES_table = D_ICD_PROCEDURES_table.astype({"icd_code": str})
        D_ICD_PROCEDURES_table['icd_code'] = [f'icd{v}|{c}' for v, c in zip(D_ICD_PROCEDURES_table['icd_version'].values, D_ICD_PROCEDURES_table['icd_code'].values)]
        D_ICD_PROCEDURES_table = D_ICD_PROCEDURES_table.drop(columns=["icd_version"])

        # preprocess
        D_ICD_PROCEDURES_table = D_ICD_PROCEDURES_table.dropna()
        D_ICD_PROCEDURES_table = D_ICD_PROCEDURES_table.drop_duplicates(subset=["icd_code"])  # NOTE: some icd codes have multiple long titles
        D_ICD_PROCEDURES_table = D_ICD_PROCEDURES_table.drop_duplicates(subset=["long_title"])  # NOTE: some long titles have multiple icd codes

        # save csv
        D_ICD_PROCEDURES_table = D_ICD_PROCEDURES_table.reset_index(drop=False)
        D_ICD_PROCEDURES_table = D_ICD_PROCEDURES_table.rename(columns={"index": "row_id"})  # add row_id
        D_ICD_PROCEDURES_table["row_id"] = range(len(D_ICD_PROCEDURES_table))
        D_ICD_PROCEDURES_table.to_csv(os.path.join(self.out_dir, "d_icd_procedures.csv"), index=False)
        self.D_ICD_PROCEDURES_dict = {item: val for item, val in zip(D_ICD_PROCEDURES_table["icd_code"].values, D_ICD_PROCEDURES_table["long_title"].values)}

        """
        d_labitems
        """
        # read csv
        D_LABITEMS_table = read_csv(
            data_dir=self.data_dir,
            filename="hosp/d_labitems.csv",
            columns=["itemid", "label"],
            lower=True,
        )

        # preprocess
        D_LABITEMS_table = D_LABITEMS_table.dropna(subset=["label"])
        filtered_label = []
        for label in D_LABITEMS_table['label'].unique():
            if label in _keep_label and _keep_label[label] != 'labevents':
                continue
            filtered_label.append(label)
        D_LABITEMS_table = D_LABITEMS_table[D_LABITEMS_table['label'].isin(filtered_label)]

        # save csv
        D_LABITEMS_table = D_LABITEMS_table.reset_index(drop=False)
        D_LABITEMS_table = D_LABITEMS_table.rename(columns={"index": "row_id"})  # add row_id
        D_LABITEMS_table["row_id"] = range(len(D_LABITEMS_table))
        D_LABITEMS_table.to_csv(os.path.join(self.out_dir, "d_labitems.csv"), index=False)
        self.D_LABITEMS_dict = {item: val for item, val in zip(D_LABITEMS_table["itemid"].values, D_LABITEMS_table["label"].values)}

        """
        d_items
        """
        # read csv
        D_ITEMS_table = read_csv(
            data_dir=self.data_dir,
            filename="icu/d_items.csv",
            columns=["itemid", "label", "abbreviation", "linksto"],
            lower=True,
        )

        # preprocess
        D_ITEMS_table = D_ITEMS_table.dropna(subset=["label"])
        D_ITEMS_table = D_ITEMS_table[D_ITEMS_table["linksto"].isin(["inputevents", "outputevents", "chartevents"])]
        filtered_label = []
        for label in D_ITEMS_table['label'].unique():
            if label in _keep_label and _keep_label[label] != 'inputevents':
                continue
            filtered_label.append(label)
        D_ITEMS_table = D_ITEMS_table[D_ITEMS_table['label'].isin(filtered_label)]

        # save csv
        D_ITEMS_table = D_ITEMS_table.reset_index(drop=False)
        D_ITEMS_table = D_ITEMS_table.rename(columns={"index": "row_id"})  # add row_id
        D_ITEMS_table["row_id"] = range(len(D_ITEMS_table))
        D_ITEMS_table.to_csv(os.path.join(self.out_dir, "d_items.csv"), index=False)
        self.D_ITEMS_dict = {item: val for item, val in zip(D_ITEMS_table["itemid"].values, D_ITEMS_table["label"].values)}

        print(f"d_icd_diagnoses, d_icd_procedures, d_labitems, d_items processed (took {round(time.time() - start_time, 4)} secs)")

    def build_diagnosis_table(self):
        print("Processing diagnoses_icd table")
        start_time = time.time()

        # read csv
        DIAGNOSES_ICD_table = read_csv(
            data_dir=self.data_dir,
            filename="hosp/diagnoses_icd.csv",
            columns=["subject_id", "hadm_id", "icd_version", "icd_code"],
            lower=True,
        )
        DIAGNOSES_ICD_table['icd_code'] = [f'icd{v}|{c}' for v, c in zip(DIAGNOSES_ICD_table['icd_version'].values, DIAGNOSES_ICD_table['icd_code'].values)]
        DIAGNOSES_ICD_table = DIAGNOSES_ICD_table.drop(columns=["icd_version"])

        # preprocess
        DIAGNOSES_ICD_table = DIAGNOSES_ICD_table.dropna(subset=["icd_code"])
        DIAGNOSES_ICD_table["charttime"] = [
            self.HADM_ID2admtime_dict[hadm] if hadm in self.HADM_ID2admtime_dict else None for hadm in DIAGNOSES_ICD_table["hadm_id"].values
        ]  # NOTE: assume charttime is at the hospital admission

        DIAGNOSES_ICD_table = DIAGNOSES_ICD_table[DIAGNOSES_ICD_table["icd_code"].isin(self.D_ICD_DIAGNOSES_dict)]

        # de-identification
        if self.deid:
            DIAGNOSES_ICD_table = self.condition_value_shuffler(DIAGNOSES_ICD_table, target_cols=["icd_code"])

        DIAGNOSES_ICD_table = DIAGNOSES_ICD_table[DIAGNOSES_ICD_table["hadm_id"].isin(self.hadm_list)]

        # timeshift
        if self.timeshift:
            DIAGNOSES_ICD_table["charttime"] = adjust_time(DIAGNOSES_ICD_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            DIAGNOSES_ICD_table = DIAGNOSES_ICD_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in DIAGNOSES_ICD_table["charttime"].values])
            DIAGNOSES_ICD_table = DIAGNOSES_ICD_table[TIME >= self.start_pivot_datetime]

        # save csv
        DIAGNOSES_ICD_table = DIAGNOSES_ICD_table.reset_index(drop=False)
        DIAGNOSES_ICD_table = DIAGNOSES_ICD_table.rename(columns={"index": "row_id"})
        DIAGNOSES_ICD_table["row_id"] = range(len(DIAGNOSES_ICD_table))
        DIAGNOSES_ICD_table.to_csv(os.path.join(self.out_dir, "diagnoses_icd.csv"), index=False)

        print(f"diagnoses_icd processed (took {round(time.time() - start_time, 4)} secs)")

    def build_procedure_table(self):
        print("Processing procedures_icd table")
        start_time = time.time()

        # read csv
        PROCEDURES_ICD_table = read_csv(
            data_dir=self.data_dir,
            filename="hosp/procedures_icd.csv",
            columns=["subject_id", "hadm_id", "icd_code", "icd_version", "chartdate"],
            lower=True,
        )
        PROCEDURES_ICD_table['icd_code'] = [f'icd{v}|{c}' for v, c in zip(PROCEDURES_ICD_table['icd_version'].values, PROCEDURES_ICD_table['icd_code'].values)]
        PROCEDURES_ICD_table = PROCEDURES_ICD_table.drop(columns=["icd_version"])

        # NOTE: In MIMIC-IV, only px table has chartdate column, not charttime / here, we use charttime column
        PROCEDURES_ICD_table["charttime"] = pd.to_datetime(PROCEDURES_ICD_table["chartdate"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        PROCEDURES_ICD_table["admittime_"] = [self.HADM_ID2admtime_dict[hadm] if hadm in self.HADM_ID2admtime_dict else None for hadm in PROCEDURES_ICD_table["hadm_id"].values]
        PROCEDURES_ICD_table["dischtime_"] = [self.HADM_ID2dischtime_dict[hadm] if hadm in self.HADM_ID2dischtime_dict else None for hadm in PROCEDURES_ICD_table["hadm_id"].values]
        # charttime = charttime if charttime in [admission, discharge] else discharge_time
        PROCEDURES_ICD_table.loc[
            (PROCEDURES_ICD_table["charttime"] < PROCEDURES_ICD_table["admittime_"]) | (PROCEDURES_ICD_table["charttime"] > PROCEDURES_ICD_table["dischtime_"]), "charttime"
        ] = PROCEDURES_ICD_table["dischtime_"]
        # clean columns
        PROCEDURES_ICD_table = PROCEDURES_ICD_table.drop(columns=["chartdate", "admittime_", "dischtime_"])

        PROCEDURES_ICD_table = PROCEDURES_ICD_table[PROCEDURES_ICD_table["icd_code"].isin(self.D_ICD_PROCEDURES_dict)]

        # de-identification
        if self.deid:
            PROCEDURES_ICD_table = self.condition_value_shuffler(table=PROCEDURES_ICD_table, target_cols=["icd_code"])

        PROCEDURES_ICD_table = PROCEDURES_ICD_table[PROCEDURES_ICD_table["hadm_id"].isin(self.hadm_list)]

        # timeshift
        if self.timeshift:
            PROCEDURES_ICD_table["charttime"] = adjust_time(PROCEDURES_ICD_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            PROCEDURES_ICD_table = PROCEDURES_ICD_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in PROCEDURES_ICD_table["charttime"].values])
            PROCEDURES_ICD_table = PROCEDURES_ICD_table[TIME >= self.start_pivot_datetime]

        # save csv
        PROCEDURES_ICD_table = PROCEDURES_ICD_table.reset_index(drop=False)
        PROCEDURES_ICD_table = PROCEDURES_ICD_table.rename(columns={"index": "row_id"})
        PROCEDURES_ICD_table["row_id"] = range(len(PROCEDURES_ICD_table))
        PROCEDURES_ICD_table.to_csv(os.path.join(self.out_dir, "procedures_icd.csv"), index=False)

        print(f"procedures_icd processed (took {round(time.time() - start_time, 4)} secs)")

    def build_labevent_table(self):
        print("Processing labevents table")
        start_time = time.time()

        # read csv
        LABEVENTS_table = read_csv(
            data_dir=self.data_dir,
            filename="hosp/labevents.csv",
            columns=["subject_id", "hadm_id", "itemid", "charttime", "valuenum", "valueuom"],
            lower=True,
        )
        LABEVENTS_table = LABEVENTS_table.dropna(subset=["hadm_id", "valuenum", "valueuom"])

        LABEVENTS_table = LABEVENTS_table[LABEVENTS_table["itemid"].isin(self.D_LABITEMS_dict)]

        # de-identification
        if self.deid:
            LABEVENTS_table = self.condition_value_shuffler(table=LABEVENTS_table, target_cols=["itemid", "valuenum", "valueuom"])

        LABEVENTS_table = LABEVENTS_table[LABEVENTS_table["hadm_id"].isin(self.hadm_list)]

        # timeshift
        if self.timeshift:
            LABEVENTS_table["charttime"] = adjust_time(LABEVENTS_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            LABEVENTS_table = LABEVENTS_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in LABEVENTS_table["charttime"].values])
            LABEVENTS_table = LABEVENTS_table[TIME >= self.start_pivot_datetime]

        # save csv
        LABEVENTS_table = LABEVENTS_table.reset_index(drop=False)
        LABEVENTS_table = LABEVENTS_table.rename(columns={"index": "row_id"})
        LABEVENTS_table["row_id"] = range(len(LABEVENTS_table))
        LABEVENTS_table.to_csv(os.path.join(self.out_dir, "labevents.csv"), index=False)

        print(f"labevents processed (took {round(time.time() - start_time, 4)} secs)")

    def build_prescriptions_table(self):
        print("Processing prescriptions table")
        start_time = time.time()

        PRESCRIPTIONS_table = read_csv(
            data_dir=self.data_dir,
            filename="hosp/prescriptions.csv",
            columns=["subject_id", "hadm_id", "starttime", "stoptime", "drug", "dose_val_rx", "dose_unit_rx", "route"],
            lower=True,
        )
        filtered_label = []
        for label in PRESCRIPTIONS_table['drug'].unique():
            if label in _keep_label and _keep_label[label] != 'prescriptions':
                continue
            filtered_label.append(label)
        PRESCRIPTIONS_table = PRESCRIPTIONS_table[PRESCRIPTIONS_table['drug'].isin(filtered_label)]
        
        PRESCRIPTIONS_table = PRESCRIPTIONS_table.dropna(subset=["starttime", "stoptime", "dose_val_rx", "dose_unit_rx", "route"])
        PRESCRIPTIONS_table["dose_val_rx"] = [int(str(v).replace(",", "")) if str(v).replace(",", "").isnumeric() else None for v in PRESCRIPTIONS_table["dose_val_rx"].values]
        PRESCRIPTIONS_table = PRESCRIPTIONS_table.dropna(subset=["dose_val_rx"])  # remove not int elements

        drug2unit_dict = {}
        for item, unit in zip(PRESCRIPTIONS_table["drug"].values, PRESCRIPTIONS_table["dose_unit_rx"].values):
            if item in drug2unit_dict:
                drug2unit_dict[item].append(unit)
            else:
                drug2unit_dict[item] = [unit]
        drug_name2unit_dict = {item: Counter(drug2unit_dict[item]).most_common(1)[0][0] for item in drug2unit_dict}  # pick only the most frequent unit of measure

        PRESCRIPTIONS_table = PRESCRIPTIONS_table[PRESCRIPTIONS_table["drug"].isin(drug2unit_dict)]
        PRESCRIPTIONS_table = PRESCRIPTIONS_table[PRESCRIPTIONS_table["dose_unit_rx"] == [drug_name2unit_dict[drug] for drug in PRESCRIPTIONS_table["drug"]]]

        # de-identification
        if self.deid:
            PRESCRIPTIONS_table = self.condition_value_shuffler(PRESCRIPTIONS_table, target_cols=["drug", "dose_val_rx", "dose_unit_rx", "route"])

        PRESCRIPTIONS_table = PRESCRIPTIONS_table[PRESCRIPTIONS_table["hadm_id"].isin(self.hadm_list)]

        # timeshift
        if self.timeshift:
            PRESCRIPTIONS_table["starttime"] = adjust_time(PRESCRIPTIONS_table, "starttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            PRESCRIPTIONS_table["stoptime"] = adjust_time(PRESCRIPTIONS_table, "stoptime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            PRESCRIPTIONS_table = PRESCRIPTIONS_table.dropna(subset=["starttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in PRESCRIPTIONS_table["starttime"].values])
            PRESCRIPTIONS_table = PRESCRIPTIONS_table[TIME >= self.start_pivot_datetime]

        # save csv
        PRESCRIPTIONS_table = PRESCRIPTIONS_table.reset_index(drop=False)
        PRESCRIPTIONS_table = PRESCRIPTIONS_table.rename(columns={"index": "row_id"})
        PRESCRIPTIONS_table["row_id"] = range(len(PRESCRIPTIONS_table))
        PRESCRIPTIONS_table.to_csv(os.path.join(self.out_dir, "prescriptions.csv"), index=False)

        print(f"prescriptions processed (took {round(time.time() - start_time, 4)} secs)")

    def build_cost_table(self):
        print("Processing COST table")
        start_time = time.time()

        DIAGNOSES_ICD_table = read_csv(self.out_dir, "diagnoses_icd.csv").astype({"icd_code": str})
        LABEVENTS_table = read_csv(self.out_dir, "labevents.csv")
        PROCEDURES_ICD_table = read_csv(self.out_dir, "procedures_icd.csv").astype({"icd_code": str})
        PRESCRIPTIONS_table = read_csv(self.out_dir, "prescriptions.csv")

        cnt = 0
        data_filter = []
        mean_costs = self.rng.poisson(lam=10, size=4)

        cost_id = cnt + np.arange(len(DIAGNOSES_ICD_table))
        person_id = DIAGNOSES_ICD_table["subject_id"].values
        hospitaladmit_id = DIAGNOSES_ICD_table["hadm_id"].values
        cost_event_table_concept_id = DIAGNOSES_ICD_table["row_id"].values
        charge_time = DIAGNOSES_ICD_table["charttime"].values
        diagnosis_cost_dict = {item: round(self.rng.normal(loc=mean_costs[0], scale=1.0), 2) for item in sorted(DIAGNOSES_ICD_table["icd_code"].unique())}
        cost = [diagnosis_cost_dict[item] for item in DIAGNOSES_ICD_table["icd_code"].values]
        temp = pd.DataFrame(
            data={
                "row_id": cost_id,
                "subject_id": person_id,
                "hadm_id": hospitaladmit_id,
                "event_type": "diagnoses_icd",
                "event_id": cost_event_table_concept_id,
                "chargetime": charge_time,
                "cost": cost,
            }
        )
        cnt += len(DIAGNOSES_ICD_table)
        data_filter.append(temp)

        cost_id = cnt + np.arange(len(LABEVENTS_table))
        person_id = LABEVENTS_table["subject_id"].values
        hospitaladmit_id = LABEVENTS_table["hadm_id"].values
        cost_event_table_concept_id = LABEVENTS_table["row_id"].values
        charge_time = LABEVENTS_table["charttime"].values
        lab_cost_dict = {item: round(self.rng.normal(loc=mean_costs[1], scale=1.0), 2) for item in sorted(LABEVENTS_table["itemid"].unique())}
        cost = [lab_cost_dict[item] for item in LABEVENTS_table["itemid"].values]
        temp = pd.DataFrame(
            data={
                "row_id": cost_id,
                "subject_id": person_id,
                "hadm_id": hospitaladmit_id,
                "event_type": "labevents",
                "event_id": cost_event_table_concept_id,
                "chargetime": charge_time,
                "cost": cost,
            }
        )
        cnt += len(LABEVENTS_table)
        data_filter.append(temp)

        cost_id = cnt + np.arange(len(PROCEDURES_ICD_table))
        person_id = PROCEDURES_ICD_table["subject_id"].values
        hospitaladmit_id = PROCEDURES_ICD_table["hadm_id"].values
        cost_event_table_concept_id = PROCEDURES_ICD_table["row_id"].values
        charge_time = PROCEDURES_ICD_table["charttime"].values
        procedure_cost_dict = {item: round(self.rng.normal(loc=mean_costs[2], scale=1.0), 2) for item in sorted(PROCEDURES_ICD_table["icd_code"].unique())}
        cost = [procedure_cost_dict[item] for item in PROCEDURES_ICD_table["icd_code"].values]
        temp = pd.DataFrame(
            data={
                "row_id": cost_id,
                "subject_id": person_id,
                "hadm_id": hospitaladmit_id,
                "event_type": "procedures_icd",
                "event_id": cost_event_table_concept_id,
                "chargetime": charge_time,
                "cost": cost,
            }
        )
        cnt += len(PROCEDURES_ICD_table)
        data_filter.append(temp)

        cost_id = cnt + np.arange(len(PRESCRIPTIONS_table))
        person_id = PRESCRIPTIONS_table["subject_id"].values
        hospitaladmit_id = PRESCRIPTIONS_table["hadm_id"].values
        cost_event_table_concept_id = PRESCRIPTIONS_table["row_id"].values
        charge_time = PRESCRIPTIONS_table["starttime"].values
        prescription_cost_dict = {item: round(self.rng.normal(loc=mean_costs[3], scale=1.0), 2) for item in sorted(PRESCRIPTIONS_table["drug"].unique())}
        cost = [prescription_cost_dict[item] for item in PRESCRIPTIONS_table["drug"].values]
        temp = pd.DataFrame(
            data={
                "row_id": cost_id,
                "subject_id": person_id,
                "hadm_id": hospitaladmit_id,
                "event_type": "prescriptions",
                "event_id": cost_event_table_concept_id,
                "chargetime": charge_time,
                "cost": cost,
            }
        )
        cnt += len(PRESCRIPTIONS_table)
        data_filter.append(temp)

        COST_table = pd.concat(data_filter, ignore_index=True)
        COST_table.to_csv(os.path.join(self.out_dir, "cost.csv"), index=False)

        print(f"cost processed (took {round(time.time() - start_time, 4)} secs)")

    def build_chartevent_table(self):
        print("Processing chartevents table")
        start_time = time.time()

        CHARTEVENTS_table_dtype = {
            "subject_id": int,
            "hadm_id": int,
            "stay_id": int,
            "charttime": str,
            "itemid": int,
            "valuenum": float,
            "valueuom": str,
        }

        CHARTEVENTS_table = read_csv(
            data_dir=self.data_dir,
            filename="icu/chartevents.csv",
            dtype={
                "subject_id": int,
                "hadm_id": int,
                "stay_id": int,
                "charttime": str,
                "itemid": str,  # int,
                "valuenum": "float64",
                "valueuom": str,
            },
            columns=["subject_id", "hadm_id", "stay_id", "charttime", "itemid", "valuenum", "valueuom"],
            lower=True,
            filter_dict={"itemid": self.chartevent2itemid.values(), "subject_id": self.patient_list},
            memory_efficient=False, # MODIFIED
        )

        CHARTEVENTS_table = CHARTEVENTS_table.dropna()
        CHARTEVENTS_table = CHARTEVENTS_table.astype(CHARTEVENTS_table_dtype)

        if self.timeshift:  # change the order due to the large number of rows in CHARTEVENTS_table
            CHARTEVENTS_table["charttime"] = adjust_time(CHARTEVENTS_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            CHARTEVENTS_table = CHARTEVENTS_table.dropna(subset=["charttime"])

        # de-identification
        if self.deid:
            CHARTEVENTS_table = self.condition_value_shuffler(CHARTEVENTS_table, target_cols=["itemid", "valuenum", "valueuom"])

        CHARTEVENTS_table = CHARTEVENTS_table[CHARTEVENTS_table["hadm_id"].isin(self.hadm_list)]

        # timeshift
        if self.timeshift:
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in CHARTEVENTS_table["charttime"].values])
            CHARTEVENTS_table = CHARTEVENTS_table[TIME >= self.start_pivot_datetime]

        # save csv
        CHARTEVENTS_table = CHARTEVENTS_table.reset_index(drop=False)
        CHARTEVENTS_table = CHARTEVENTS_table.rename(columns={"index": "row_id"})
        CHARTEVENTS_table["row_id"] = range(len(CHARTEVENTS_table))
        CHARTEVENTS_table.to_csv(os.path.join(self.out_dir, "chartevents.csv"), index=False)

        print(f"chartevents processed (took {round(time.time() - start_time, 4)} secs)")

    def build_inputevent_table(self):
        print("Processing inputevents table")
        start_time = time.time()

        INPUTEVENTS_table = read_csv(
            data_dir=self.data_dir,
            filename="icu/inputevents.csv",
            columns=["subject_id", "hadm_id", "stay_id", "starttime", "itemid", "amount", "amountuom"],
            lower=True,
        )

        INPUTEVENTS_table = INPUTEVENTS_table.dropna(subset=["hadm_id", "stay_id", "amount", "amountuom"])
        INPUTEVENTS_table = INPUTEVENTS_table[INPUTEVENTS_table["amountuom"] == "ml"]  # Input volume is mostly (~50%) in ml
        del INPUTEVENTS_table["amountuom"]

        INPUTEVENTS_table = INPUTEVENTS_table[INPUTEVENTS_table["itemid"].isin(self.D_ITEMS_dict)]

        # de-identification
        if self.deid:
            INPUTEVENTS_table = self.condition_value_shuffler(table=INPUTEVENTS_table, target_cols=["itemid", "amount"])

        INPUTEVENTS_table = INPUTEVENTS_table[INPUTEVENTS_table["hadm_id"].isin(self.hadm_list)]

        # timeshift
        if self.timeshift:
            INPUTEVENTS_table["starttime"] = adjust_time(INPUTEVENTS_table, "starttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            INPUTEVENTS_table = INPUTEVENTS_table.dropna(subset=["starttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in INPUTEVENTS_table["starttime"].values])
            INPUTEVENTS_table = INPUTEVENTS_table[TIME >= self.start_pivot_datetime]

        # save csv
        INPUTEVENTS_table = INPUTEVENTS_table.reset_index(drop=False)
        INPUTEVENTS_table = INPUTEVENTS_table.rename(columns={"index": "row_id"})
        INPUTEVENTS_table["row_id"] = range(len(INPUTEVENTS_table))
        INPUTEVENTS_table.to_csv(os.path.join(self.out_dir, "inputevents.csv"), index=False)

        print(f"inputevents processed (took {round(time.time() - start_time, 4)} secs)")

    def build_outputevent_table(self):
        print("Processing outputevents table")
        start_time = time.time()

        # read csv
        OUTPUTEVENTS_table = read_csv(
            data_dir=self.data_dir,
            filename="icu/outputevents.csv",
            columns=["subject_id", "hadm_id", "stay_id", "charttime", "itemid", "value", "valueuom"],
            lower=True,
        )

        # preprocess
        OUTPUTEVENTS_table = OUTPUTEVENTS_table.dropna(subset=["hadm_id", "stay_id", "value", "valueuom"])
        OUTPUTEVENTS_table = OUTPUTEVENTS_table[OUTPUTEVENTS_table["valueuom"] == "ml"]  # Output volume is always in ml
        del OUTPUTEVENTS_table["valueuom"]

        OUTPUTEVENTS_table = OUTPUTEVENTS_table[OUTPUTEVENTS_table["itemid"].isin(self.D_ITEMS_dict)]

        # de-identification
        if self.deid:
            OUTPUTEVENTS_table = self.condition_value_shuffler(
                table=OUTPUTEVENTS_table,
                target_cols=["itemid", "value"],
            )

        OUTPUTEVENTS_table = OUTPUTEVENTS_table[OUTPUTEVENTS_table["hadm_id"].isin(self.hadm_list)]

        # timeshift
        if self.timeshift:
            OUTPUTEVENTS_table["charttime"] = adjust_time(OUTPUTEVENTS_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id")
            OUTPUTEVENTS_table = OUTPUTEVENTS_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in OUTPUTEVENTS_table["charttime"].values])
            OUTPUTEVENTS_table = OUTPUTEVENTS_table[TIME >= self.start_pivot_datetime]

        # save csv
        OUTPUTEVENTS_table = OUTPUTEVENTS_table.reset_index(drop=False)
        OUTPUTEVENTS_table = OUTPUTEVENTS_table.rename(columns={"index": "row_id"})
        OUTPUTEVENTS_table["row_id"] = range(len(OUTPUTEVENTS_table))
        OUTPUTEVENTS_table.to_csv(os.path.join(self.out_dir, "outputevents.csv"), index=False)

        print(f"outputevents processed (took {round(time.time() - start_time, 4)} secs)")

    def build_microbiology_table(self):
        print("Processing microbiologyevents table")
        start_time = time.time()

        # read csv
        MICROBIOLOGYEVENTS_table = read_csv(
            data_dir=self.data_dir,
            filename="hosp/microbiologyevents.csv",
            columns=["subject_id", "hadm_id", "chartdate", "charttime", "spec_type_desc", "test_name", "org_name"],
            lower=True,
        )

        # If charttime is null, use chartdate as charttime
        MICROBIOLOGYEVENTS_table["charttime"] = MICROBIOLOGYEVENTS_table["charttime"].fillna(MICROBIOLOGYEVENTS_table["chartdate"])
        del MICROBIOLOGYEVENTS_table["chartdate"]

        # de-identification
        if self.deid:
            MICROBIOLOGYEVENTS_table = self.condition_value_shuffler(
                table=MICROBIOLOGYEVENTS_table,
                target_cols=["spec_type_desc", "test_name", "org_name"],
            )

        MICROBIOLOGYEVENTS_table = MICROBIOLOGYEVENTS_table[MICROBIOLOGYEVENTS_table["hadm_id"].isin(self.hadm_list)]

        # timeshift
        if self.timeshift:
            MICROBIOLOGYEVENTS_table["charttime"] = adjust_time(
                MICROBIOLOGYEVENTS_table, "charttime", current_time=self.current_time, offset_dict=self.subjectid2admittime_dict, patient_col="subject_id"
            )
            MICROBIOLOGYEVENTS_table = MICROBIOLOGYEVENTS_table.dropna(subset=["charttime"])
            TIME = np.array([datetime.strptime(tt, "%Y-%m-%d %H:%M:%S") for tt in MICROBIOLOGYEVENTS_table["charttime"].values])
            MICROBIOLOGYEVENTS_table = MICROBIOLOGYEVENTS_table[TIME >= self.start_pivot_datetime]

        # save csv
        MICROBIOLOGYEVENTS_table = MICROBIOLOGYEVENTS_table.reset_index(drop=False)
        MICROBIOLOGYEVENTS_table = MICROBIOLOGYEVENTS_table.rename(columns={"index": "row_id"})
        MICROBIOLOGYEVENTS_table["row_id"] = range(len(MICROBIOLOGYEVENTS_table))
        MICROBIOLOGYEVENTS_table.to_csv(os.path.join(self.out_dir, "microbiologyevents.csv"), index=False)

        print(f"microbiologyevents processed (took {round(time.time() - start_time, 4)} secs)")


    def generate_db(self):

        rows = read_csv(self.out_dir, "patients.csv")
        rows.to_sql("patients", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "admissions.csv")
        rows.to_sql("admissions", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "d_icd_diagnoses.csv").astype({"icd_code": str})
        rows.to_sql("d_icd_diagnoses", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "d_icd_procedures.csv").astype({"icd_code": str})
        rows.to_sql("d_icd_procedures", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "d_items.csv")
        rows.to_sql("d_items", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "d_labitems.csv")
        rows.to_sql("d_labitems", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "diagnoses_icd.csv").astype({"icd_code": str})
        rows.to_sql("diagnoses_icd", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "procedures_icd.csv").astype({"icd_code": str})
        rows.to_sql("procedures_icd", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "labevents.csv")
        rows.to_sql("labevents", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "prescriptions.csv")
        rows.to_sql("prescriptions", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "cost.csv")
        rows.to_sql("cost", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "chartevents.csv")
        rows.to_sql("chartevents", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "inputevents.csv")
        rows.to_sql("inputevents", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "outputevents.csv")
        rows.to_sql("outputevents", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "microbiologyevents.csv")
        rows.to_sql("microbiologyevents", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "icustays.csv")
        rows.to_sql("icustays", self.conn, if_exists="append", index=False)

        rows = read_csv(self.out_dir, "transfers.csv")
        rows.to_sql("transfers", self.conn, if_exists="append", index=False)

        query = "SELECT * FROM sqlite_master WHERE type='table'"
        print(pd.read_sql_query(query, self.conn)["name"])  # 17 tables

    def _check_assertion_db_and_csv(self, table_names=None):
        if table_names is None:
            table_names = pd.read_sql_query("SELECT * FROM sqlite_master WHERE type='table'", self.conn)["name"]

        for table_name in table_names:
            table_name = table_name.lower()
            csv = read_csv(self.out_dir, f"{table_name}.csv")
            db = pd.read_sql_query(f"select * from {table_name}", self.conn)

            # np.nan => None object (for comparison)
            csv = csv.where(pd.notnull(csv), None)
            db = db.where(pd.notnull(db), None)
            assert set(csv.columns) == set(db.columns.str.lower())
            csv = csv[db.columns.str.lower()]

            assert csv.shape == db.shape
            try:
                if (csv.values == db.values).all():
                    pass
                elif table_name == "prescriptions":
                    pass  # data types of dose_val_rx is not the same
                else:
                    raise AssertionError(f"csv and db are not the same: {table_name}")
            except:
                breakpoint()
