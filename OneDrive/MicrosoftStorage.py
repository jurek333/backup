import json
import requests
import logging
import OneDrive
import BaseStorage.Driver
import BaseStorage.ProgramConfiguration
from time import localtime, strftime, strptime
from pathlib import Path


class OneDriveStorage(BaseStorage.Driver):

    def __init__(self, configuration: BaseStorage.ProgramConfiguration):
        self.urls = OneDrive.MicrosoftConfiguration()
        self.resource_url = self.urls.RESOURCE + "/v1.0/me/drive/root"
        self.config = configuration
        self.auth = OneDrive.Authentication(self.get_one_drive_configuration(self.config))
        self.header = {"Authorization": self.auth.get_authentication_header()}

        self.config.update_file()

    def make_get(self, url: str):
        resp = requests.get(url, headers=self.header)
        logging.debug("[OneDrive] the GET request to {} finished with status code {}."
            .format(url, resp.status_code))
        if resp.status_code == 401:
            self.header = {"Authorization": self.auth.authentication_error()}
            self.config.update_file()
            resp = requests.get(url, headers = self.header)
            logging.debug("[OneDrive] the GET request to {} finished with status code {}."
                .format(url, resp.status_code))
        if resp.status_code == 404:
            return None
        data = resp.json()
        return data

    def make_put(self, url:str, body:object):
        resp = requests.put(url, data=body, headers = self.header)
        logging.debug("[OneDrive] the PUT request to {} finished with status code {}"
                .format(url,resp.status_code))
        if resp.status_code == 401:
            self.header = {"Authorization": self.auth.authentication_error()}
            self.config.update_file()
            resp = requests.put(url, data=body, headers = self.header)
            logging.debug("[OneDrive] the PUT request to {} finished with status code {}"
                    .format(url,resp.status_code))

    def get_one_drive_configuration(self, config):
        if "one_drive" in config.data:
            return OneDrive.OneDriveConfiguration(config.data["one_drive"])
        else:
            return None

    def get_root_folders(self):
        url = self.urls.RESOURCE + "/v1.0/me/drive/root/children"
        dir_list = self.make_get(url)
        return dir_list

    def get_file_info(self, path: Path):
        url = self.resource_url + ":"+ path.as_posix()
        file_info = self.make_get(url)
        return file_info

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

    def save(self, path, trg) -> bool:
        webPath = (path / trg.name)
        file_info = self.get_file_info(webPath)
        if file_info is not None:
            print("Znaleziono {} (ostatnio zmodyfikowany {})"
                    .format(
                        file_info["name"],
                        file_info["lastModifiedDateTime"]))
            choose = input("Czy chcesz go nadpisać (T), czy zmodyfikować nazwę (M)? [T/M/N]: ".format(file_info))
            if choose == 'M' or choose == 'm':
                webPath = path / (trg.stem + strftime(" (%Y %m %d %H %M %S)", localtime()) + trg.suffix)
            else:
                if choose == 'N' or choose == 'n':
                    return False;
        url = self.resource_url + ":" + webPath.as_posix() + ":/content"
        with trg.open("rb") as f:
            body = f.read()
        resp = self.make_put(url, body)
        return True

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
