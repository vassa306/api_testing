import string
import random
import uuid

import pytest
from jsonschema import validate, ValidationError
from faker import Faker


class CommonUtility:
    class CommonUtility:
        """
        A utility class providing common helper methods for API testing, data validation,
        random data generation, and JSON schema validation.

        Attributes:
            f (Faker): An instance of the Faker library for generating random test data.

        Methods:
            get_custom_header() -> dict:
                Returns a custom header for API requests.

            generate_random_user() -> tuple:
                Generates a random username and email.

            generateRandomString(length: int = 3) -> str:
                Generates a random alphanumeric string of a given length.

            generate_params(data: dict) -> dict:
                Returns the input data unchanged (placeholder for parameter generation logic).

            is_valid_uuid_list(uuid_list: list, version: int = 4) -> bool:
                Validates if all elements in the given list are valid UUIDs of the specified version.

            is_expected_string(list_values: list) -> bool:
                Checks if all elements in the given list are non-empty strings.

            is_expected_double(list_values: list) -> bool:
                Checks if all elements in the given list are valid non-negative floating-point numbers.

            generate_random_uuid() -> str:
                Generates and returns a random UUID.

            extract_barrel_id(barrel_id: str) -> str:
                Pytest fixture to extract a barrel ID.

            is_double(value: any) -> bool:
                Checks if the given value is a non-negative float.

            extract_values(data: list[dict], key: str) -> list:
                Extracts values for a specific key from a list of dictionaries.

            is_valid_response(response: any) -> bool:
                Validates if the response is a list of dictionaries.

            validate_json(data: dict, schema: dict, schema_name: str = "JSON") -> bool:
                Validates JSON data against a given schema.

            validate_data(actual_data: dict, expected_data: dict, keys: list = None) -> None:
                Validates that actual data matches expected data for specified keys.
        """

    f = Faker()

    @staticmethod
    def get_custom_header():
        header = {
            'Accept': 'application/json'  # Corrected format (dict)
        }
        return header

    @staticmethod
    def get_custom_inv_header():
        header = {
            'aaaaa': 'application/xxxx'
        }
        return header

    @staticmethod
    def generate_random_user():
        username = CommonUtility.f.user_name()
        email = CommonUtility.f.email()
        return username, email

    @staticmethod
    def generateRandomString(length=3):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def generate_params(data):
        return data

    @staticmethod
    def is_valid_uuid_list(uuid_list, version=4):
        if not isinstance(uuid_list, list):
            return False  # Ensure input is a list

        for uuid_to_test in uuid_list:
            try:
                # Validate UUID
                uuid_obj = uuid.UUID(str(uuid_to_test), version=version)
            except (ValueError, TypeError):
                return False
        return True

    @staticmethod
    def is_expected_string(list_values):
        if not isinstance(list_values, list):  # Check if input is a list
            return False

        for str_val in list_values:
            if not isinstance(str_val, str) or len(str_val) < 1:  # Ensure it's a non-empty string
                return False

        return True

    @staticmethod
    def is_expected_double(list_values):
        """
           Checks if the given input is a list containing only non-negative floating-point numbers.

           Args:
               list_values (any): The input value to be checked.

           Returns:
               bool: True if the input is a list where all elements are non-negative floats, otherwise False.
        """
        if not isinstance(list_values, list):  # Check if input is a list
            return False

        for double_val in list_values:
            if not isinstance(double_val, float) and double_val >= 0:  # Ensure it's a non-empty string
                return False
        return True

    @staticmethod
    def generate_random_uuid():
        random_uuid = str(uuid.uuid4())
        return random_uuid

    @staticmethod
    def is_double(value):
        """
           Checks if the given value is a non-negative floating-point number.

           Args:
               value (any): The value to be checked.

           Returns:
               bool: True if the value is a float and greater than or equal to zero, otherwise False.
           """
        return isinstance(value, float) and value >= 0

    @staticmethod
    def extract_values(data: list[dict], key: str) -> list:
        """
           Extracts values associated with a specific key from a list of dictionaries.

           Args:
               data (list[dict]): A list of dictionaries from which values will be extracted.
               key (str): The key whose values need to be retrieved.

           Returns:
               list: A list of values corresponding to the given key in each dictionary.
                     If a dictionary does not contain the key, it is skipped.
           """
        return [item.get(key) for item in data if key in item]

    @staticmethod
    def is_valid_response(response: any) -> bool:
        """
            Validates whether the given response is a list containing only dictionaries.

            Args:
                response (any): The response to validate.

            Returns:
                bool: True if the response is a list of dictionaries, otherwise False.
        """
        return isinstance(response, list) and all(isinstance(item, dict) for item in response)

    @staticmethod
    def validate_json(data, schema, schema_name="JSON"):
        """
        Validates JSON data against a given schema.

        Args:
            data (dict): The JSON response to validate.
            schema (dict): The JSON Schema to validate against.
            schema_name (str): Optional name for better error reporting.

        Raises:
            pytest.fail: If validation fails.
        """
        try:
            validate(instance=data, schema=schema)
            print("{schema_name} response is valid")
            return True
        except ValidationError as e:
            print(f"{schema_name} response validation failed: {e.message}")
            return False

    @staticmethod
    def validate_data(actual_data, expected_data, keys=None):
        """
        Validates that the actual data matches the expected data for specified keys.

        Args:
            actual_data (dict): The actual response data received from the API.
            expected_data (dict): The expected data for comparison.
            keys (list, optional): A list of keys to validate. If None, all keys in `expected_data` will be used.

        Raises:
            AssertionError: If any attribute does not match the expected value.
        """
        keys_to_check = keys if keys else expected_data.keys()  # Default to all keys in expected_data
        for key in keys_to_check:
            assert actual_data[key] == expected_data[
                key], f"Mismatch in '{key}': Expected {expected_data[key]}, got {actual_data[key]}"
