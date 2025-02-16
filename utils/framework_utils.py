import pytest
import requests as requests


class FrameworkUtils:
    """
        A utility class for making API requests with custom headers and validating the response status.

        Methods:
            fire_api_with_cust_headers(request_method='GET', request_url=None, request_param=None,
            request_json=None, headers=None, expected_status_code=200) -> requests.Response:
            Sends an HTTP request with optional parameters, JSON body, and headers, and verifies the
            response status code.
    """

    @staticmethod
    def fire_api_with_cust_headers(request_method='GET', request_url=None,
                                   request_param=None,
                                   request_json=None,
                                   headers=None,
                                   expected_status_code=200):
        """
            Sends an API request using the specified HTTP method, headers, parameters, and JSON body.
            Validates that the response status code matches the expected status.

            Args:
                request_method (str, optional): The HTTP method (GET, POST, PUT, DELETE, etc.). Defaults to 'GET'.
                request_url (str, optional): The API endpoint URL.
                request_param (dict, optional): Query parameters to be sent with the request. Defaults to None.
                request_json (dict, optional): JSON payload to be sent in the request body. Defaults to None.
                headers (dict, optional): HTTP headers to include in the request. Defaults to None.
                expected_status_code (int, optional): The expected HTTP status code for the response.
                Defaults to 200.

            Returns:
                requests.Response: The response object from the API request.

            Raises:
                AssertionError: If the actual response status code does not match the expected status code.
                pytest.fail: If the API call fails due to an unexpected response status code.
        """
        response = requests.request(request_method,
                                    request_url,
                                    params=request_param,
                                    json=request_json,
                                    headers=headers)
        try:
            assert response.status_code == expected_status_code, f"expected code is {expected_status_code} " \
                                                                 f"but found {response.status_code}"
            return response
        except:
            pytest.fail(f"Api call failed status code was {response.status_code} ")
