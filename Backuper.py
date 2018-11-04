from pathlib import Path
import logging
from ConfigurationReader import ConfigurationReader
import OneDrive
import BaseStorage

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

    def check_target(self, target:Path) -> bool:
        is_dir = target.is_dir()
        is_file = target.exists()
        return is_file or is_dir

    def load_mapping(self):
        map_path = Path("/") / self.root_folder / self.map_file_name
        logging.debug("[Conf] ładuję plik mapowania: %s"%(map_path.as_posix()))
        map_file_content = self.storage.load_file(map_path)
        return map_file_content

    def backup(self, target, labels):
        # 0. check if target exists
        if False == self.check_target(target):
            return (False, "{} doesn't exists - check target".format(target))
        # 1. get mapping
        mapping = self.load_mapping()
        if "map" not in mapping:
            return (False, "configuration file is missing map section")
        keys = []
        paths = [];
        # 2. find paths
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
            p = Path('/') / self.root_folder / mapping["map"][key]["path"]
            paths.append(p)
        logging.debug("[B] paths: {}".format(paths))
        if len(paths)==0:
            return (False, "none of labels {} has mapped path to it".format(labels))

        # 3. save files
        result = True
        for path in paths:
            result = result and self.storage.save(path, target)
        return (result,"")
