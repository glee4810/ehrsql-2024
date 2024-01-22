python3 preprocess_db.py \
--data_dir /nfs_data_storage/mimic-iv-2.2-demo \
--db_name mimic_iv \
--num_patient 100 \
--timeshift \
--current_time "2100-12-31 23:59:00" \
--start_year 2100 \
--time_span 0 \
--cur_patient_ratio 0.1