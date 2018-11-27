import argparse
import logging

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("rootlabel")
    parser.add_argument("-l", "--log",
            help="log level that will be shown on screen (default INFO)",
            default="INFO",
            choices=["DEBUG", "INFO", "WARN", "ERROR"])
    args = parser.parse_args()
    return (args.rootlabel, args.log)

def set_logging(log_level):
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: {}".format(log_level))
    logging.basicConfig(format="%(message)s", level=numeric_level)

def main():
    root, log_level = get_args()
    set_logging(log_level)
    logging.info("Listing backup labels")

if __name__ == "__main__":
    main()
