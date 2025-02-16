import json
import os


class FunctionalParam:
    """
     A utility class for handling API endpoint configurations.

     Attributes:
         BASE_DIR (str): The base directory path of the current file.
         FILE_PATH (str): The path to the JSON configuration file containing API endpoints.

     Methods:
         get_base_end_point() -> str:
             Reads the API base endpoint from the configuration file based on the current environment.
     """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = os.path.join(BASE_DIR, "..", "config", "endpoints.json")

    @staticmethod
    def get_base_end_point():
        with open(FunctionalParam.FILE_PATH, "r", encoding="utf-8") as conf_file:
            properties = json.load(conf_file)
            env = properties["environment"]["env"]
            return properties[env]["base_url"]
