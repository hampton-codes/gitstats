import json
import logging

# Setup logging
logger = logging.getLogger('gitstats')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# Flatten the json by concat of keys
def json_to_csv(json_data, fields):
    ret_data = []
    
    field_list = set()
    for field in fields:
        field_list.add(field)
    
    output = []
    for item in json_data:
        element = {}
        for field in fields:
            if field.find('.') > 0:
                drill_down = field.split('.')
                element[f'{drill_down[0]}.{drill_down[1]}'] = item[drill_down[0]][drill_down[1]]
            else:
                element[field] = item[field]
        if item['languages']:
            for key in item['languages'].keys():
                element[f'languages.{key}'] = item['languages'][key]
                field_list.add(f'languages.{key}')
        output.append(element)
    header_line = ''
    for field in field_list:
        header_line = f'{header_line},{field}'
    ret_data.append(header_line[1:])
    for out in output:
        line = ''
        for field in field_list:
            line = f'{line},{out[field]}'
        ret_data.append(line[1:])

# print data
def print_output(data, fields, mode):
    if not data:
        return
    if mode == "csv":
        print(json_to_csv(data, fields))
    else:
        print(json.dumps(data, indent=4))
