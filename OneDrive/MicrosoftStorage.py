import json
import requests
import logging
import OneDrive
import BaseStorage.Driver
import BaseStorage.ProgramConfiguration


class OneDriveStorage(BaseStorage.Driver):

    def __init__(self, configuration: BaseStorage.ProgramConfiguration):
        self.urls = OneDrive.MicrosoftConfiguration()
        auth = OneDrive.Authentication(self.get_one_drive_configuration(configuration))
        token = auth.authenticate()
        self.header = {"Authorization": token}
        configuration.update_file()
    
    def get_one_drive_configuration(self, config):
        if "one_drive" in config.data:
            return OneDrive.OneDriveConfiguration(config.data["one_drive"])
        else:
            return None

    def get_root_folders(self):
        url = self.urls.RESOURCE + "/v1.0/me/drive/root/children"
        dir_list = requests.get(url, headers=self.header).json()
        print(json.dumps(dir_list, indent=4))
        return dir_list

    def create_folder(self, name, path=""):
        url = self.urls.RESOURCE + "/v1.0/me/drive/root" + path + "/children"
        body = {
            "name":name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        resp = requests.post(url, json=body, headers = self.header)
        if resp.status_code != 201:
            logging.error("Creating main folder failed")
            logging.debug(resp)
            return None
        return resp.json()
