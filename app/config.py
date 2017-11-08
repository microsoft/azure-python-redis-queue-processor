"""
    config.py only contains the configuration class
"""
import os
import json

class Config(object):
    """
    This class contains configuration parameters for all applications
    """
    def __init__(self, config_file="config.json"):
        with open(config_file, "rt") as conf:
            self.__dict__ = json.loads(conf.read())