import os
import requests
import argparse
import json
import logging
from sys import platform, argv
import time
import OneDrive
import BaseStorage

APP_NAME = argv[0]

class ConfigurationReader:
    def get_configuration_path(self):
        if platform == "linux" or platform == "linux2":
            return "~/.backuprc"
        elif platform == "win32" or platform == "win64":
            return os.getenv("USERPROFILE") + "\\_backuprc"
        else:
            return None
            
class Backuper:
    def __init__(self, driver: BaseStorage.Driver):
        self.root_folder = "BackupAccessMemory"
        self.storage = driver #OneDriveStorage(token_header)

    def get_root_folder():
        folders = self.storage.get_root_folders()
        for f in folders:
            if f["name"] == self.root_folder:
                return f
        f = self.storage.create_folder(self.storage.root_folder)
        return f

    def backup(self, target, labels):
        print("In the future I will save %s under %s"%(target, labels))


def get_args(conf: BaseStorage.ProgramConfiguration):
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("labels", nargs="+")
    parser.add_argument("-l", "--log"
            , help="log level that sould be logged on screen (default INFO)"
            , default="INFO"
            , choices=["DEBUG","INFO","WARN","ERROR"])
    args = parser.parse_args()
    conf.log_level = args.log
    return (args.file, args.labels)

def set_logging(log_level):
    level = getattr(logging, log_level.upper(), None)
    if not isinstance(level, int):
        raise ValueError("Invalid log level: %s"%(log_level))
    logging.basicConfig(format="%(message)s", level=level)

if __name__ == "__main__":
    # read configuration
    conf_path = ConfigurationReader().get_configuration_path()
    conf = BaseStorage.ProgramConfiguration(conf_path).load()
    if conf is None:
        logging.error("Configuration file was not found. Please provide valid configuration")
        exit(1)
    # read arguments
    target, labels = get_args(conf)
    set_logging(conf.log_level)
    # initialize choosen storage driver
    driver = OneDrive.OneDriveStorage(conf)
    if driver is None:
        logging.error("The storage driver failed to initilize.")
        exit(1)
    # pass it to buckuper
    backup = Backuper(driver)
    # do backup job
    result = backup.backup(target, labels)
    if result == False:
        logging.error("Fail to store %s"%(target))        
    
    logging.info("The target: %s was stored and labeled: %s"%(target, labels))
