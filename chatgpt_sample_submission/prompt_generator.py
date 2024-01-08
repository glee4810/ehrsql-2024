import pandas as pd

def load_schema(DATASET_JSON):
    schema_df = pd.read_json(DATASET_JSON)
    schema_df = schema_df.drop(['column_names','table_names'], axis=1)
    schema = []
    f_keys = []
    p_keys = []
    for index, row in schema_df.iterrows():
        tables = row['table_names_original']
        col_names = row['column_names_original']
        col_types = row['column_types']
        foreign_keys = row['foreign_keys']
        primary_keys = row['primary_keys']
        for col, col_type in zip(col_names, col_types):
            index, col_name = col
            if index > -1:
                schema.append([row['db_id'], tables[index], col_name, col_type])
        for primary_key in primary_keys:
            index, column = col_names[primary_key]
            p_keys.append([row['db_id'], tables[index], column])
        for foreign_key in foreign_keys:
            first, second = foreign_key
            first_index, first_column = col_names[first]
            second_index, second_column = col_names[second]
            f_keys.append([row['db_id'], tables[first_index], tables[second_index], first_column, second_column])
    db_schema = pd.DataFrame(schema, columns=['Database name', 'Table Name', 'Field Name', 'Type'])
    primary_key = pd.DataFrame(p_keys, columns=['Database name', 'Table Name', 'Primary Key'])
    foreign_key = pd.DataFrame(f_keys,
                        columns=['Database name', 'First Table Name', 'Second Table Name', 'First Table Foreign Key',
                                 'Second Table Foreign Key'])
    return db_schema, primary_key, foreign_key

def find_foreign_keys_MYSQL_like(foreign, db_id):
  df = foreign[foreign['Database name'] == db_id]
  output = "["
  for index, row in df.iterrows():
    output += row['First Table Name'] + '.' + row['First Table Foreign Key'] + " = " + row['Second Table Name'] + '.' + row['Second Table Foreign Key'] + ', '
  output= output[:-2] + "]"
  if len(output)==1:
      output = '[]'
  return output

def find_fields_MYSQL_like(db_schema, db_id):
  df = db_schema[db_schema['Database name'] == db_id]
  df = df.groupby('Table Name')
  output = ""
  for name, group in df:
    output += "Table " +name+ ', columns = ['
    for index, row in group.iterrows():
        output += row["Field Name"]+', '
    output = output[:-2]
    output += "]\n"
  return output

def create_schema_prompt(db_id, db_schema, primary_key, foreign_key, is_lower=True):
    prompt = find_fields_MYSQL_like(db_schema, db_id)
    prompt += "Foreign_keys = " + find_foreign_keys_MYSQL_like(foreign_key, db_id)
    if is_lower:
        prompt = prompt.lower()
    return prompt
