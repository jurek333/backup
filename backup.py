import argparse
import logging
from ConfigurationReader import ConfigurationReader
from Backuper import Backuper
import OneDrive
import BaseStorage

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

def main():
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
    result, errormsg = backup.backup(target, labels)
    if result == False:
        logging.error("Fail to store %s: %s"%(target, errormsg))
    else:
        logging.info("The target: %s was stored and labeled: %s"%(target, labels))

if __name__ == "__main__":
    main()
