import json
import os

import pytest


def pytest_addoption(parser):
    parser.addoption("--host", action="store", default="prod")


def update_env(config):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH = os.path.join(BASE_DIR, "config", "endpoints.json")
    with open(FILE_PATH, "r+", encoding="utf-8") as jsonFile:
        try:
            # Read existing JSON data
            data = json.load(jsonFile)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in endpoints.json")

        print(f"Before update: {data}")

        # Ensure 'environment' key exists
        if "environment" not in data:
            raise KeyError("'environment' key is missing in endpoints.json")

        # Update environment value
        data["environment"]["env"] = config.getoption("--host").lower()

        # Move to start and clear the file before writing updated JSON
        jsonFile.seek(0)
        jsonFile.truncate()
        json.dump(data, jsonFile, indent=4)


@pytest.hookimpl()
def pytest_configure(config):
    update_env(config)
