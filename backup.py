import os
import requests
import argparse
import json
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
            print("Configuration file exists.")
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
                print("all ok")
            else:
                print("Nie masz pełnych praw RW do pliku %s"%(confPath))
                print("Zmień uprawnienia na pliku.")
                return None
        else:
            print("Brak pliku configuracji.")
            print("Użyj %s configure"%(APP_NAME))
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
    reader = ConfigurationReader()
    conf = reader.load()
    odconf = conf.get_one_drive_configuration()
    
    auth = OneDrive.Authentication(odconf)
    auth.run_authentication()


