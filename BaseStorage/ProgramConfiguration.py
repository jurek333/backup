import os
import logging
import json

class ProgramConfiguration:
    def __init__(self, file_path):
        self.log_level = "INFO"
        self.configuration_file_path = file_path
    
    def load(self):
        if os.path.isfile(self.configuration_file_path):
            if os.access(self.configuration_file_path, os.R_OK | os.W_OK):
                logging.debug("file exists and We have permissions")
            else:
                logging.warn("you haven't exact permissions %s"%(self.configuration_file_path))
                return None
        else:
            logging.info("file doesn't exist")
            return None

        with open(self.configuration_file_path, 'r') as f:
            config = json.loads(f.read())
            self.data = config
        
        return self
        
    def update_file(self):
        if os.path.isfile(self.configuration_file_path):
            if os.access(self.configuration_file_path, os.R_OK | os.W_OK):
                logging.debug("file exists and We have permissions")
            else:
                logging.warn("you haven't exact permissions %s"%(self.configuration_file_path))
                return False
        else:
            logging.info("file doesn't exist")
            return False

        with open(self.configuration_file_path, 'w') as f:
            #print(json.dumps(self.data, indent=2))
            f.write(json.dumps(self.data, indent=2))
        return True
