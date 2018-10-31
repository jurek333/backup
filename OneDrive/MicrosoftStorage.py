import json
import requests
import logging
import OneDrive
import BaseStorage.Driver
import BaseStorage.ProgramConfiguration


class OneDriveStorage(BaseStorage.Driver):

    def __init__(self, configuration: BaseStorage.ProgramConfiguration):
        self.urls = OneDrive.MicrosoftConfiguration()
        self.resource_url = self.urls.RESOURCE + "/v1.0/me/drive/root"
        self.config = configuration
        self.auth = OneDrive.Authentication(self.get_one_drive_configuration(self.config))
        self.header = {"Authorization": self.auth.get_authentication_header()}

        self.config.update_file()

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

    def load_file(self, path):
        url = self.resource_url +":"+ path.as_posix() + ":/content"
        resp = requests.get(url, headers = self.header)
        logging.debug("[OD] load file from {} with status code {}".format(url, resp.status_code))
        if resp.status_code == 401:
            self.header = {"Authorization": self.auth.authentication_error()}
            self.config.update_file()
            resp = requests.get(url, headers = self.header)
            logging.debug("[OD] load file from {} with status code {}".format(url, resp.status_code))
        data = resp.json()
        return data

    def save(self, path, trg):
        url = self.resource_url + ":" + (path / trg.name).as_posix() + ":/content"
        with trg.open() as f:
            body = f.read()
        resp = requests.put(url, data=body, headers = self.header)
        logging.debug("save under {} returned {}".format(url,resp.status_code))
        if resp.status_code == 401:
            self.header = {"Authorization": self.auth.authentication_error()}
            self.config.update_file()
            resp = requests.put(url, headers = self.header)

    def create_folder(self, name, path=""):
        url = self.resource_url + path + "/children"
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
