import os
from pathlib import PurePath
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
        self.root_folder = "RAM"
        self.map_file_name = "treasuremap.json"
        self.storage = driver #OneDriveStorage(token_header)

    def get_root_folder():
        folders = self.storage.get_root_folders()
        for f in folders:
            if f["name"] == self.root_folder:
                return f
        f = self.storage.create_folder(self.storage.root_folder)
        return f

    def check_target(self, target) -> bool:
        is_dir = False
        is_file = os.path.isfile(target)
        if is_file == False:
            is_dir = os.path.isdir(target)
        return is_file or is_dir

    def load_mapping(self):
        map_path = PurePath("/") / self.root_folder / self.map_file_name
        logging.debug("[Conf] ładuję plik mapowania: %s"%(str(map_path)))
        map_file_content = self.storage.load_file(str(map_path))
        return map_file_content

    def backup(self, target, labels):
        print("In the future I will save %s under %s"%(target, labels))
        # 0. check if target exists
        if False == self.check_target(target):
            return (False, "{} doesn't exists - check target".format(target))
        # 1. get mapping
        mapping = self.load_mapping()
        # 2. find paths
        # 3. save files
        # 4. 
        return (True,"")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("labels", nargs="+")
    parser.add_argument("-l", "--log"
            , help="log level that sould be logged on screen (default INFO)"
            , default="INFO"
            , choices=["DEBUG","INFO","WARN","ERROR"])
    args = parser.parse_args()
    return (args.file, args.labels, args.log)

def set_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s"%(log_level))
    logging.basicConfig(format="%(message)s", level=numeric_level)

if __name__ == "__main__":
    # read arguments
    target, labels, log_level = get_args()
    set_logging(log_level)
    # read configuration
    conf_path = ConfigurationReader().get_configuration_path()
    conf = BaseStorage.ProgramConfiguration(conf_path).load()
    conf.log_level = log_level
    if conf is None:
        logging.error("Configuration file was not found. Please provide valid configuration")
        exit(1)
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
