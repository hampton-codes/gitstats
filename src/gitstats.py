import sys
import json
import argparse

# Local file imports
import configreader
from utils import logger, print_output
from git import handle_repository, handle_organization

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
    
    # Assemble the data
    data = []
    if args.repository:
        data = [handle_repository(args.repository, headers, fields, args.nolanguages)]
    elif args.organization:
        data = handle_organization(args.organization, headers, fields, args.nolanguages)
    elif args.user:
        data = handle_organization(args.user, headers, fields, args.nolanguages, user_repos=True)
    else:
        print("Yay.... No work to do!")
        print("To exercise me specify either repository or organization to scan.")
    
    # Output the data
    print_output(data, fields, args.mode)

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
        help="all github org repos (eg: --org=hampton-codes)")
    parser.add_argument("-u", "--user",
        help="all github user repos (eg: --user=hampton-codes)")
    parser.add_argument("-nl", "--nolanguages",
        help="collect language stats", action="store_true")
    parser.add_argument("-m", "--mode", default="json",
        help="output format. Values: (json|csv)")
    args = parser.parse_args()
    
    # Do work
    main(args)