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
