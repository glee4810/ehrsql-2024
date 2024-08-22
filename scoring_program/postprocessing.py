import re

CURRENT_DATE = "2100-12-31"
CURRENT_TIME = "23:59:00"
NOW = f"{CURRENT_DATE} {CURRENT_TIME}"
PRECOMPUTED_DICT = {
    'temperature': (35.5, 38.1),
    'sao2': (95.0, 100.0),
    'heart rate': (60.0, 100.0),
    'respiration': (12.0, 18.0),
    'systolic bp': (90.0, 120.0),
    'diastolic bp': (60.0, 90.0),
    'mean bp': (60.0, 110.0)
}
TIME_PATTERN = r"(DATE_SUB|DATE_ADD)\((\w+\(\)|'[^']+')[, ]+ INTERVAL (\d+) (MONTH|YEAR|DAY)\)"

def convert_date_function(match):
    function = match.group(1)
    date = match.group(2)
    number = match.group(3)
    unit = match.group(4).lower()
    
    # Use singular form when number is 1
    if number == '1':
        unit = unit.rstrip('s')
    else:
        unit += 's' if not unit.endswith('s') else ''
    
    # Determine the sign based on the function (DATE_SUB or DATE_ADD)
    sign = '-' if function == 'DATE_SUB' else '+'
    
    return f"datetime({date}, '{sign}{number} {unit}')"

def post_process_sql(query):

    query = re.sub('[ ]+', ' ', query.replace('\n', ' ')).strip()
    query = query.replace('> =', '>=').replace('< =', '<=').replace('! =', '!=')

    # Convert MySQL to SQLite functions
    query = re.sub(TIME_PATTERN, convert_date_function, query)

    if "current_time" in query: # strftime('%J',current_time) => strftime('%J','2100-12-31 23:59:00')
        query = query.replace("current_time", f"'{NOW}'")
    if "current_date" in query: # strftime('%J',current_date) => strftime('%J','2100-12-31')
        query = query.replace("current_date", f"'{CURRENT_DATE}'")
    if "'now'" in query: # 'now' => '2100-12-31 23:59:00'
        query = query.replace("'now'", f"'{NOW}'")
    if "NOW()" in query: # NOW() => '2100-12-31 23:59:00'
        query = query.replace("NOW()", f"'{NOW}'")
    if "CURDATE()" in query: # CURDATE() => '2100-12-31'
        query = query.replace("CURDATE()", f"'{CURRENT_DATE}'")
    if "CURTIME()" in query: # CURTIME() => '23:59:00'
        query = query.replace("CURTIME()", f"'{CURRENT_TIME}'")
        
    if re.search('[ \n]+([a-zA-Z0-9_]+_lower)', query) and re.search('[ \n]+([a-zA-Z0-9_]+_upper)', query):
        vital_lower_expr = re.findall('[ \n]+([a-zA-Z0-9_]+_lower)', query)[0]
        vital_upper_expr = re.findall('[ \n]+([a-zA-Z0-9_]+_upper)', query)[0]
        vital_name_list = list(set(re.findall('([a-zA-Z0-9_]+)_lower', vital_lower_expr) + re.findall('([a-zA-Z0-9_]+)_upper', vital_upper_expr)))
        if len(vital_name_list)==1:
            processed_vital_name = vital_name_list[0].replace('_', ' ')
            if processed_vital_name in PRECOMPUTED_DICT:
                vital_range = PRECOMPUTED_DICT[processed_vital_name]
                query = query.replace(vital_lower_expr, f"{vital_range[0]}").replace(vital_upper_expr, f"{vital_range[1]}")

    query = query.replace("%y", "%Y").replace('%j', '%J')

    return query
