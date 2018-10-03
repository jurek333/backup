import os
import requests
import argparse
import json
import logging
from sys import platform, argv
import time
import OneDrive

APP_NAME = argv[0]

class ConfigurationReader:
    def getConfigurationPath(self):
        if platform == "linux" or platform == "linux2":
            return "~/.backuprc"
        elif platform == "win32" or platform == "win64":
            return os.getenv("USERPROFILE") + "\\_backuprc"
        else:
            return None

    def __init__(self):
        confPath = self.getConfigurationPath()
        if os.path.isfile(confPath):
            logging.debug("configuration file exists")
        else:
            defConf = {
                "backupFolder":"ROM",
                "lastUpdate":time.asctime(),
                "token":"",
                "refresh_token":"",
                "token_type":"Bearer",
                "client_id":"",
                "client_secret":"",
                "registered_redirect_url":""
            }
            with open(confPath, 'w') as f:
                f.write(defConf)
        return
   
    def load(self):
        confPath = self.getConfigurationPath()
        if os.path.isfile(confPath):
            if os.access(confPath, os.R_OK | os.W_OK):
                logging.debug("file exists and We have permissions")
            else:
                logging.warn("you haven't exact permissions %s"%(confPath))
                return None
        else:
            logging.info("file doesn't exist")
            return None

        with open(confPath, 'r') as f:
            config = json.loads(f.read())
        
        return Configuration(config)
    
class Configuration:

    def __init__(self, data):
       self.data = data

    def get_one_drive_configuration(self):
        if "one_drive" in self.data:
            return OneDrive.OneDriveConfiguration(self.data["one_drive"])
        else:
            return None
            
       

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log")
    args = parser.parse_args()

    log_level = getattr(logging, args.log.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError("Invalid log level: %s"%(args.log))
    logging.basicConfig(format="%(levelname)s:%(message)s", level=log_level)

    logging.debug("starting the program")
    reader = ConfigurationReader()
    conf = reader.load()
    logging.debug("configuration has been read")
    odconf = conf.get_one_drive_configuration()
    logging.debug("start authentication")
    auth = OneDrive.Authentication(odconf)
    auth.run_authentication()
    logging.debug("authentication succedded")


