import argparse
import logging
from ConfigurationReader import ConfigurationReader
from Backuper import Backuper
import OneDrive
import BaseStorage
import json

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log"
            , help="log level that sould be logged on screen (default INFO)"
            , default="INFO"
            , choices=["DEBUG","INFO","WARN","ERROR"])
    subparsers = parser.add_subparsers()

    save_parser = subparsers.add_parser("save")
    save_parser.add_argument("file")
    save_parser.add_argument("labels", nargs="+")
    save_parser.set_defaults(command="save")

    label_parser = subparsers.add_parser("label")
    label_parser.add_argument("--list", action="store_true")
    label_parser.add_argument("parent_labels", nargs="*")
    label_parser.set_defaults(command="label")

    args = parser.parse_args()
    return args

def set_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s"%(log_level))
    logging.basicConfig(format="%(message)s", level=numeric_level)

def save(args):
    # read configuration
    conf_path = ConfigurationReader().get_configuration_path()
    conf = BaseStorage.ProgramConfiguration(conf_path).load()
    conf.log_level = args.log
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
    result, errormsg = backup.backup(args.file, args.labels)
    if result == False:
        logging.error("Fail to store %s: %s"%(args.file, errormsg))
    else:
        logging.info("The target: %s was stored and labeled: %s"%(args.file, args.labels))

def label(args):
    print("here will be implementation of label command")

def main():
    args = get_args()
    set_logging(args.log)
    if args.command == "save":
        save(args)
    elif args.command == "label":
        label(args)


if __name__ == "__main__":
    main()
