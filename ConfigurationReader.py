import os
from sys import platform

class ConfigurationReader:
    def get_configuration_path(self):
        if platform == "linux" or platform == "linux2":
            return "~/.backuprc"
        elif platform == "win32" or platform == "win64":
            return os.getenv("USERPROFILE") + "\\_backuprc"
        else:
            return None
