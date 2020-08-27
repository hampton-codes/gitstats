import time
import json
import datetime
import requests
from utils import logger

GIT_BASE_URL = 'https://api.github.com'
THROTTLE = 10
SLEEP_TIME = 2

# Get data from single repository
def handle_repository(rep, headers, fields, ignore_languages):
    data = {}
    json_data = {}

    url = f'{GIT_BASE_URL}/repos/{rep}'
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            json_data = json.loads(r.text)
            for field in fields:
                # Only support one level of nexted structure at this time
                if(field.find('.') > 0):
                    drill_down = field.split('.')
                    if not drill_down[0] in data.keys():
                        data[drill_down[0]] = {}
                    data[drill_down[0]][drill_down[1]] = json_data[drill_down[0]][drill_down[1]]
                else:
                    data[field] = json_data[field]
        else:
            logger.warn(f'Hmm... non HTTP 200/OK code received')
            logger.warn(f'    URL: {url}')
            logger.warn(f'    Status code: {r.status_code}')
            logger.warn(f'    Response: {r.text}')
            return data
    except requests.RequestException as e:
        logger.error(f'Error making call to github! {url}')
        logger.exception(e)
    
    if data and not ignore_languages:
        data['languages'] = get_repo_languages(json_data['languages_url'], headers)
    
    return data

# Get just languages
def get_repo_languages(url, headers):
    languages = {}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            json_data = json.loads(r.text)
            for key in json_data.keys():
                languages[key] = json_data[key]
        else:
            logger.warn(f'Hmm... non HTTP 200/OK code received')
            logger.warn(f'    URL: {url}')
            logger.warn(f'    Status code: {r.status_code}')
            logger.warn(f'    Response: {r.text}')
    except requests.RequestException as e:
        logger.error(f'Error making call to github! {url}')
        logger.exception(e)
    return languages      

# Iterate through the org or users repositories
def handle_organization(org, headers, fields, ignore_languages, user_repos=False):
    all_data = []
    throttle_counter = 0
    
    if user_repos:
        url = f'{GIT_BASE_URL}/users/{org}/repos'
    else:
        url = f'{GIT_BASE_URL}/orgs/{org}/repos'
    
    # list repos in user/organization
    try:
        while(url):
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                json_data = json.loads(r.text)
                ## TODO: Handle pagination and iterate through the pages
                for repo in json_data:
                    data = {}
                    for field in fields:
                        # Only support one level of nexted structure at this time
                        if(field.find('.') > 0):
                            drill_down = field.split('.')
                            if not drill_down[0] in data.keys():
                                data[drill_down[0]] = {}
                            data[drill_down[0]][drill_down[1]] = repo[drill_down[0]][drill_down[1]]
                        else:
                            data[field] = repo[field]
                    if data and not ignore_languages:
                        data['languages'] = get_repo_languages(repo['languages_url'], headers)
                    if data:
                        all_data.append(data)
                    throttle_counter += 1
                    if throttle_counter > THROTTLE:
                        throttle_counter = 0
                        time.sleep(SLEEP_TIME)
                if "next" in r.links.keys():
                    url = r.links['next']['url']
                else:
                    url = None
            elif r.status_code == 403:
                utcnow = datetime.datetime.utcnow().strftime('%s')
                reset_timestamp = r.headers.get('X-RateLimit-Reset')
                time_left = int(reset_timestamp) - int(utcnow)
                logger.debug(f'X-RateLimit-Reset: {reset_timestamp}')
                reset_time = datetime.datetime.utcfromtimestamp(reset_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
            
                logger.warn('Hmm... HTTP 403/Forbidden. Bad token or rate limit?!')
                logger.warn(f'    Rate limit remaining {r.headers.get("X-RateLimit-Remaining")} of {r.headers.get("X-RateLimit-Limit")}')
                logger.warn(f'    Will reset at {reset_time}. In about {time_left} seconds')
                if(int(r.headers.get("X-RateLimit-Remaining")) == 0):
                    time.sleep(SLEEP_TIME)
                else:
                    url = None
            elif r.status_code == 404:
                logger.warn(f'Hmm... HTTP 404/Not Found')
                logger.warn(f'    URL: {url}')
                logger.warn(f'    Status code: {r.status_code}')
                logger.warn(f'    Response: {r.text}')
                logger.warn(f'    Hint: Perhaps this is a user account not organization')
            else:
                logger.warn(f'Hmm... non HTTP 200/OK code received')
                logger.warn(f'    URL: {url}')
                logger.warn(f'    Status code: {r.status_code}')
                logger.warn(f'    Response: {r.text}')
    except requests.RequestException as e:
        logger.error(f'Error making call to github! {url}')
        logger.exception(e)
        
    return all_data