import sys
import json
import requests
import argparse

# Local file imports
import configreader
from utils import logger

GIT_BASE_URL = 'https://api.github.com'

# Get data from repository
def handle_repository(rep, headers, fields, ignore_languages):
    data = {}
    csv_data = {}

    url = f'{GIT_BASE_URL}/repos/{rep}'
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            json_data = json.loads(r.text)
            for field in fields:
                # Only support one level of nexted structure at this time
                if(field.find('.') > 0):
                    drill_down = field.split('.')
                    data[drill_down[0]] = {}
                    data[drill_down[0]][drill_down[1]] = json_data[drill_down[0]][drill_down[1]]
                    csv_data[field] = json_data[drill_down[0]][drill_down[1]]
                else:
                    data[field] = json_data[field]
                    csv_data[field] = json_data[field]
        else:
            logger.warn(f'Hmm... non HTTP 200/OK code received')
            logger.warn(f'    URL: {url}')
            logger.warn(f'    Status code: {r.status_code}')
            logger.warn(f'    Response: {r.text}')
            return data, csv_data
    except Exception as e:
        logger.error(f'Error making call to github! {url}')
        logger.exception(e)
    
    if not ignore_languages:
        data['languages'] = {}
        url = json_data['languages_url']
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                json_data = json.loads(r.text)
                for key in json_data.keys():
                    data['languages'][key] = json_data[key]
                    csv_data[f'languages.{key}'] = json_data[key]
            else:
                logger.warn(f'Hmm... non HTTP 200/OK code received')
                logger.warn(f'    URL: {url}')
                logger.warn(f'    Status code: {r.status_code}')
                logger.warn(f'    Response: {r.text}')
                return data, csv_data
        except Exception as e:
            logger.error(f'Error making call to github! {url}')
            logger.exception(e)
    
    return data, csv_data

# Do work
def main(args):
    # Read configuration file
    conf = configreader.parse(args.config)
    if not conf:
        sys.exit(1)
    
    # Get list of fields
    if args.fields:
        fields = args.fields.split(',')
    else:
        try:
            fields = conf['default']['fields'].split(',')
        except Exception as e:
            logger.error(f'Config missing `fields` in [default] section!')
            logger.exception(e)
            sys.exit(2)
    
    # Get github config for auth
    try:
        if conf['github']['token']:
            headers = {
                'Authorization': f'token {conf["github"]["token"]}',
                'Accept': 'application/json'
            }
    except Exception as e:
        logger.error(f'Config missing `token` in [github] section')
        logger.exception(e)
        sys.exit(2)
    
    # Handle individual repository
    if args.repository:
        data, csv_data = handle_repository(args.repository, headers, fields, args.nolanguages)
        if csv_data and args.mode == "csv":
            line = ''
            header_line = ''
            for key in csv_data.keys():
                header_line = f'{header_line},{key}'
                line = f'{line},{csv_data[key]}'
            print(header_line[1:])
            print(line[1:])
        else:
            print(json.dumps(data, indent=4))
    elif args.organization:
        print("Organization scan coming soon!")
    else:
        print("Yay.... No work to do!")
        print("To exercise me specify either repository or organization to scan.")

if __name__ == '__main__':
    # Setup CLI options
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
        help="path to config file. (eg: --config=../conf/gitstats.ini)")
    parser.add_argument("-r", "--repository",
        help="path to specific repository. (eg: --repository=hampton-codes/gitstats)")
    parser.add_argument("-f", "--fields",
        help="fields to collect. comma-separated. (eg: --fields=name,owner.type)")
    parser.add_argument("-o", "--organization",
        help="github org (eg: --org=hampton-codes)")
    parser.add_argument("-nl", "--nolanguages",
        help="collect language stats", action="store_true")
    parser.add_argument("-m", "--mode", default="json",
        help="output format. Values: (json|csv)")
    args = parser.parse_args()
    
    # Do work
    main(args)