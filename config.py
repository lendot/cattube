import json

def load_config(filename):
    with open(filename) as file:
        json_data=file.read()

    config_obj = json.loads(json_data)
    return config_obj


def save_config(config_obj,filename):
    json_data = json.dumps(config_obj,indent=4)
    with open(filename,"w") as file:
        file.write(json_data)


class MurderboxConfig:
    """
    class for reading/writing Murderbox configuration
    """

    def __init__(self,config_file):
        self.config_file = config_file
        self._load()


    def _load(self):
        with open(self.config_file) as file:
            json_data=file.read()

        self.config_data = json.loads(json_data)
        

    def save(self):
        """
        save the config data to the config file
        """
        json_data = json.dumps(self.config_data,indent=4)
        with open(self.config_file,"w") as file:
            file.write(json_data)

            
    def get(self,name,default):
        """
        gets a configuration value, or the default value if not set
        """
        if name in self.config_data:
            return self.config_data[name]
        else:
            return default

        
    def set(self,name,value):
        """
        sets a configuration value
        """
        self.config_data[name] = value
