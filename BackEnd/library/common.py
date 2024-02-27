import json

def get_config_value(key):
    with open("./config/config.json", "r") as read_file:
        _config = json.load(read_file)
    return _config[key]

def get_initial_training():
    with open("./config/training.json", "r") as read_file:
        training  = json.load(read_file)
    return training