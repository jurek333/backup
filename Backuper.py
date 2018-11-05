from pathlib import Path
import logging
from ConfigurationReader import ConfigurationReader
import OneDrive
import BaseStorage

class Backuper:

    def __init__(self, driver: BaseStorage.Driver):
        self.storage = driver #OneDriveStorage(token_header)
        self.mapping = {
            "map": {
                "configuration": {"path": ""}
            }
        }

    def _check_target(self, target:Path) -> bool:
        is_dir = target.is_dir()
        is_file = target.exists()
        return is_file or is_dir

    def _get_paths(self, labels):
        keys = []
        paths = [];
        if "aliases" in mapping:
            for label in labels:
                if label in mapping["aliases"]:
                    k = mapping["aliases"][label]
                    keys.extend(k)
                else:
                    keys.append(label)
        else:
            keys = labels
        logging.debug("[B] aliases: {}".format(keys))
        for key in keys:
            if key in mapping["map"]:
                p = mapping["map"][key]["path"]
                paths.append(p)
            else:
                logging.error("The label {} is not im the mapping. File {} cannot be saved there!"
                        .format(key, target.name))
        logging.debug("[B] paths: {}".format(paths))
        return paths

    def backup(self, trg, labels):
        target = Path(trg)
        # 0. check if target exists
        if False == self._check_target(target):
            return (False, "The file {} doesn't exists - check target".format(target))
        # 1. get mapping
        mapping = self.storage.load_configuration()
        if None is not mapping:
            self.mapping = mapping
        if "map" not in mapping:
            return (False, "Configuration file is missing 'map' section")
        # 2. find paths
        paths = self._get_paths(labels)
        # 3. save files
        if len(paths)==0:
            return (False, "None of labels {} maps to paths".format(labels))
        result = True
        for path in paths:
            result = result and self.storage.save(path, target)
        return (result,"")
