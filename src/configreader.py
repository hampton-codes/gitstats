import os
import sys
import configparser

from utils import logger

DEFAULT_CONFIG_FILE='../conf/gitstats.ini'

# Parse the config file
def parse(file_name=None):
    file_name = file_name or DEFAULT_CONFIG_FILE
    if not os.path.exists(file_name):
        logger.error(f'Failed to find config file! {file_name}')
        return
    try:
        config = configparser.ConfigParser()
        config.read(file_name)
        return config
    except Exception as e:
        logger.error(f'Failed to parse config file! {file_name}')
        logger.exception(e)
        return
