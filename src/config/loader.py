import json
from pathlib import Path

def load_config():

    """
    Loads application configuration from config/config.json
    """

    project_root = Path(__file__).parents[2]    #it safely jumps to root of the project
    config_path = project_root/ "config" / "config.json"


    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    

    with open(config_path, "r") as f:
        json.load(f)            #Reads a JSON file and parses the content into a Python object.
    
if __name__ == "__main__":
    print(load_config())