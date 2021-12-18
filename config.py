import yaml

# default config file
CONFIG_FILE = "config.yaml"

class CatTubeConfig:
    """
    class for reading/writing CatTube configuration
    """

    def __init__(self,config_file = CONFIG_FILE):
        self.config_file = config_file
        self.load()


    def load(self):
        """ (Re)load configuration file """
        with open(self.config_file) as f:
            self.config_data = yaml.load(f,Loader=yaml.FullLoader)
        

    def get(self,name,default=None):
        """
        gets a configuration value, or the default value if not set
        """
        if name in self.config_data["cattube"]:
            return self.config_data["cattube"][name]
        else:
            return default

        
    def set(self,name,value):
        """
        sets a configuration value
        """
        self.config_data[name] = value
