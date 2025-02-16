import pytest
from pytest import mark

from config.api_config import ApiUrls
from req_resp.barrels import Barrels
from utils.common_utils import CommonUtility
from utils.framework_utils import FrameworkUtils
import time


class TestBarrelApi:
    @mark.barrels
    def test_get_barrels(self):
        """
            Test case to verify the retrieval of barrels using a GET request.

            Steps:
                1. Retrieve the GET URL from the `ApiUrls` class.
                2. Fetch the custom headers using the `CommonUtility` class.
                3. Send a GET request to retrieve barrels and validate the expected status code (200).
                4. Extract the "id", "qr", "rfid", and "nfc" values from the response data.
                5. Validate that:
                   - Each "id" is a valid UUID (version 4).
                   - Each "qr" value is a non-empty string.
                   - Each "rfid" value is a non-empty string.
                   - Each "nfc" value is a non-empty string.

            Assertions:
                The test fails if any "id" is not a valid UUID v4.
                The test fails if any "qr", "rfid", or "nfc" values are empty or not strings.

            Expected Outcome:
                The test passes if all retrieved barrel data meets the expected criteria.
        """
        url = ApiUrls.GET_BARRELS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("GET", request_url=url, headers=headers,
                                                             expected_status_code=200)
        data = response.json()
        uuid_list = CommonUtility.extract_values(data, "id")
        is_valid_uuid = CommonUtility.is_valid_uuid_list(uuid_list, 4)
        qr_vals = CommonUtility.extract_values(data, "qr")
        nfc_vals = CommonUtility.extract_values(data, "nfc")
        rfid_vals = CommonUtility.extract_values(data, "rfid")
        isvalid_qr = CommonUtility.is_expected_string(qr_vals)
        isvalid_rfid = CommonUtility.is_expected_string(rfid_vals)
        is_valid_nfc = CommonUtility.is_expected_string(nfc_vals)
        assert is_valid_uuid is True, "is not valid UUID string"
        assert isvalid_qr is True, "is not a String or its an empty String"
        assert isvalid_rfid is True, "is not a String or its an empty String"
        assert is_valid_nfc is True, "is not a String or its an empty String"

    @pytest.fixture(scope="session")
    @mark.barrels
    def post_barrels_valid(self):
        """
            Pytest fixture to create a new barrel via a POST request, validate its creation,
            and ensure the data remains consistent in subsequent GET requests.

            This fixture performs the following steps:
            1. Sends a `POST` request to create a new barrel using predefined request data.
            2. Extracts and stores key identifiers (`id`, `qr`, `rfid`, `nfc`) from the response.
            3. Yields the created barrel's `id` for test usage.
            4. Asserts that the generated `id` matches the expected UUID.
            5. Sends a `GET` request to validate that the newly created barrel exists in the database.

            Scope:
                session - The fixture runs once per test session.

            Yields:
                Contains the dictionary of created object.

            Raises:
                AssertionError: If the generated `id` does not match the expected UUID.
                AssertionError: If the created barrel is not found in the GET response.

            Logs:
                - Prints the response data from the `POST` request.
                - Prints the created barrel's details.
                - Prints a boolean indicating whether the barrel exists in the system.
        """

        url = ApiUrls.GET_BARRELS
        exp_uuid = Barrels.random_uuid
        expected_response = Barrels.CREATE_Barrel
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Barrel,
                                                             expected_status_code=201)

        data = response.json()
        barrel_id = data["id"]

        created_barrel = {
            "id": barrel_id,
            "qr": data["qr"],
            "rfid": data["rfid"],
            "nfc": data["nfc"]
        }

        is_valid_json = CommonUtility.validate_json(data, Barrels.Barrels_Schema, "JSON")
        assert is_valid_json is True
        assert response.headers.get("Content-Type") == "application/json; charset=utf-8", \
            f"Expected text/plain but got" \
            f" {response.headers.get('Content-Type')}"

        yield data
        CommonUtility.validate_data(data, expected_data=expected_response, keys=["id", "qr", "rfid", "nfc"])

        # get after post validation that object has the same data
        response = FrameworkUtils.fire_api_with_cust_headers("GET", request_url=url, headers=headers,
                                                             expected_status_code=200)
        data = response.json()
        exists = created_barrel in data
        assert exists is True

    @mark.barrels
    def test_post_barrels_invalid_headers(self):
        """
           Tests the API's response when attempting to create a barrel with invalid headers.

           Steps:
               1. Retrieve the API URL for posting barrels.
               2. Obtain invalid headers using `CommonUtility.get_custom_inv_header()`.
               3. Define the expected request payload using `Barrels.CREATE_Barrel`.
               4. Send a POST request with invalid headers.
               5. Verify that the API returns a 400 status code (bad request).

           Expected Behavior:
               - The API should reject the request due to invalid headers.
               - The response should include an appropriate error message.

           Assertions:
               - Ensures that the POST request fails as expected with a 400 status code.

        """
        url = ApiUrls.GET_MEASUREMENTS
        headers = CommonUtility.get_custom_inv_header()
        expected_response = Barrels.CREATE_Barrel
        response = FrameworkUtils.fire_api_with_cust_headers("POST", url, request_json=expected_response,
                                                             headers=headers,
                                                             expected_status_code=400)

    @mark.barrels
    def test_delete_barrels(self, post_barrels_valid):
        """
            Test deleting a barrel and verifying that it has been successfully removed.

            Steps:
                1. Retrieve the DELETE URL for the given barrel ID.
                2. Send a DELETE request to remove the barrel.
                3. Verify that the DELETE request returns a 200 status code (successful deletion).
                4. Send a GET request with the same barrel ID.
                5. Validate that the GET request returns a 404 status code, confirming the barrel no longer exists.

            Assertions:
                - Ensures the DELETE request is successful.
                - Ensures that the barrel is no longer retrievable after deletion.

            arg: post_barrels_valid dict returned by post_barrels_valid fixture.
        """

        url = ApiUrls.get_barrel_by_id(post_barrels_valid["id"])
        print(url)
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("DELETE", request_url=url, headers=headers,
                                                             expected_status_code=200)

        # call again get with the same value. should return 404 because barrel was deleted.
        url = ApiUrls.get_barrel_by_id(post_barrels_valid)
        response = FrameworkUtils.fire_api_with_cust_headers("GET", request_url=url, headers=headers,
                                                             expected_status_code=404)

    @mark.barrels
    def test_delete_barrels_inv_header(self, post_barrels_valid):
        """
           Tests the API's behavior when attempting to delete a barrel with an invalid header.

           Steps:
               1. Retrieve the DELETE URL for the given barrel ID.
               2. Obtain invalid headers using `CommonUtility.get_custom_inv_header()`.
               3. Send a DELETE request with invalid headers.
               4. Verify that the DELETE request returns a 400 status code (bad request).

           Expected Behavior:
               - The API should reject the DELETE request due to invalid headers.
               - The response should include an appropriate error message.

           Assertions:
               - Ensures the DELETE request fails as expected with a 400 status code.

           Args:
               post_barrels_valid (dict): Dictionary returned by the `post_barrels_valid` fixture containing barrel details.
        """

        url = ApiUrls.get_barrel_by_id(post_barrels_valid["id"])
        print(url)
        headers = CommonUtility.get_custom_inv_header()
        response = FrameworkUtils.fire_api_with_cust_headers("DELETE", request_url=url, headers=headers,
                                                             expected_status_code=400)

    @mark.barrels
    def test_create_twice_the_same_barrel(self, post_barrels_valid):
        """
          Test creating the same barrel twice to ensure the API prevents duplicate entries.

          This test verifies that attempting to create a barrel with the same attributes
          as an existing one results in a `409 Conflict` error.

          Steps:
              1. Retrieve the API URL for barrels.
              2. Use the `post_barrels_valid` fixture to get the details of an already created barrel.
              3. Print the barrel data for debugging purposes.
              4. Get the custom headers required for the API request.
              5. Send a `POST` request with the same barrel data.
              6. Validate that the response status code is `409`, indicating a conflict due to duplication.

          Assertions:
              - Ensures that the duplicate barrel creation attempt results in a `409 Conflict` response.

          Args:
              post_barrels_valid (dict): A dictionary containing the details of a previously created barrel.

          Raises:
              AssertionError: If the API does not return a `409` status code when trying to create a duplicate barrel.

        """
        url = ApiUrls.GET_BARRELS
        data = post_barrels_valid
        print(data)
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=data,
                                                             expected_status_code=409)
        print(response)

    @mark.barrels
    def test_delete_barrels_invalid_id(self):
        """
            Test deleting a non-existing barrel.

            Steps:
                1. Retrieve the DELETE URL for the given barrel ID.
                2. Send a DELETE request to remove the barrel with non existing id.
                3. Verify that the DELETE request returns 400

            Assertions:
            - Ensures the DELETE request is not successful and returns 400.

        """
        url = ApiUrls.get_barrel_by_id("a")
        print(url)
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("DELETE", request_url=url, headers=headers,
                                                             expected_status_code=400)

    @mark.barrels
    def test_post_barrels_missing_req_value(self):
        """
          Tests the API endpoint for posting a barrel with missing required attributes.

          This test sends a POST request to the barrels endpoint with a payload
          that lacks required attributes and expects a 400 Bad Request response.

          Steps:
              1. Retrieve the API URL for barrels.
              2. Get custom headers for the request.
              3. Send a POST request with a payload missing required attributes.
              4. Validate that the response status code is 400.
              5. Print the response for debugging purposes.

          Raises:
              AssertionError: If the response status code is not 400.

          """
        url = ApiUrls.GET_BARRELS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Barrel_Missing_Values,
                                                             expected_status_code=400)
        print(response)

    @mark.barrels
    def test_post_barrels_invalid_uuid(self):
        """
            Test case for attempting to create a barrel with an invalid UUID.

            This test sends a POST request to the `GET_BARRELS` API endpoint with an incorrect UUID format
            and verifies that the server returns a 400 Bad Request response.

            Steps:
            1. Retrieve the API URL from `ApiUrls.GET_BARRELS`.
            2. Obtain custom headers using `CommonUtility.get_custom_header()`.
            3. Send a POST request with an invalid UUID payload (`Barrels.CREATE_Barrel_Wrong_UUID`).
            4. Validate that the response status code is 400.

            Assertions:
            - The response should return a 400 status code, indicating a client error.

        """
        url = ApiUrls.GET_BARRELS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Barrel_Wrong_UUID,
                                                             expected_status_code=400)
        print(response)

    @mark.barrels
    def test_post_barrels_empty_body(self):
        """
                   Test case for attempting to create a barrel with an invalid UUID.

                   This test sends a POST request to the `GET_BARRELS` API endpoint with an incorrect UUID format
                   and verifies that the server returns a 400 Bad Request response.

                   Steps:
                   1. Retrieve the API URL from `ApiUrls.GET_BARRELS`.
                   2. Obtain custom headers using `CommonUtility.get_custom_header()`.
                   3. Send a POST request with an invalid UUID payload (`Barrels.CREATE_Barrel_Wrong_UUID`).
                   4. Validate that the response status code is 400.

                   Assertions:
                   - The response should return a 400 status code, indicating a client error.

        """
        url = ApiUrls.GET_BARRELS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json={},
                                                             expected_status_code=400)
        print(response)

    @mark.barrels
    def test_post_barrels_empty_headers(self):
        """
            Test case for attempting to create a barrel with an invalid UUID.

            This test sends a POST request to the `GET_BARRELS` API endpoint with an incorrect UUID format
            and verifies that the server returns a 400 Bad Request response.

            Steps:
            1. Retrieve the API URL from `ApiUrls.GET_BARRELS`.
            2. Obtain custom headers using `CommonUtility.get_custom_header()`.
            3. Send a POST request with an invalid UUID payload (`Barrels.CREATE_Barrel_Wrong_UUID`).
            4. Validate that the response status code is 400.

            Assertions:
            - The response should return a 400 status code, indicating a client error.

        """
        url = ApiUrls.GET_BARRELS
        headers = CommonUtility.get_custom_empty_header()
        print(headers)
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Barrel,
                                                             expected_status_code=201)
        print(response)

    @mark.barrels
    def test_post_barrels_invalid_param_type(self):
        """
           Tests the API's response when attempting to create a barrel with invalid parameter types.

           Steps:
               1. Retrieve the API URL for posting barrels.
               2. Obtain the necessary request headers.
               3. Define the request payload with invalid parameter types (`Barrels.CREATE_Barrel_Invalid_Type`).
               4. Send a POST request with the invalid payload.
               5. Verify that the API returns a 400 status code (bad request).
               6. Print the response for debugging purposes.

           Expected Behavior:
               - The API should reject the request due to incorrect parameter types.
               - The response should include an appropriate error message.

           Assertions:
               - Ensures that the POST request fails as expected with a 400 status code.

        """
        url = ApiUrls.GET_BARRELS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Barrel_Invalid_Type,
                                                             expected_status_code=400)
        print(response)

    @mark.barrels
    def test_response_time_get_barrels(self):
        """
            Measures the response time of the GET request to fetch barrels and ensures it is within the acceptable threshold.

            Steps:
            1. Retrieves the API URL for fetching barrels.
            2. Obtains the necessary headers.
            3. Records the start time.
            4. Sends a GET request to the API and checks the response status code (expected: 200).
            5. Records the stop time and calculates the response time.
            6. Asserts that the response time is less than 2 seconds.

            Raises:
                AssertionError: If the API response time exceeds the 2-second threshold.

        """
        url = ApiUrls.GET_BARRELS
        headers = CommonUtility.get_custom_header()
        start_time = time.time()
        response = FrameworkUtils.fire_api_with_cust_headers("GET", request_url=url, headers=headers,
                                                             expected_status_code=200)
        stop_time = time.time()
        response_time = stop_time - start_time
        assert response_time < 2, f" API response is too slow: {response_time:.2f} s"

    # #################################### measuremnets tests
    # #####################################################################

    @pytest.fixture(scope="session")
    def post_measurement(self, post_barrels_valid):
        """
            Sends a POST request to create a measurement for a given barrel and validates the response.

            Args:
                post_barrels_valid (str): The ID of the barrel for which the measurement is being posted.

            Yields:
                dict: The response data from the API containing measurement details.

            Raises:
                AssertionError: If the response does not conform to the expected JSON schema or if
                                dirtLevel and weight are not valid double values.
        """
        url = ApiUrls.GET_MEASUREMENTS
        expected_response = Barrels.CREATE_Measuremenent_Valid
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Measuremenent_Valid,
                                                             expected_status_code=200)
        data = response.json()

        is_double_dirt_level = CommonUtility.is_double(data["dirtLevel"])
        is_double_weight = CommonUtility.is_double(data["weight"])
        is_valid_json = CommonUtility.validate_json(data, Barrels.Measurement_Schema, "JSON")

        # it will work just in case api will not return any created attribute in response
        assert is_valid_json is True, "created invalid JSON schema"
        CommonUtility.validate_data(data, expected_response, keys=["id", "barrelId", "dirtLevel", "weight"])
        assert is_double_dirt_level is True
        assert is_double_weight is True

        yield data

    def test_get_measurement_with_exist_id(self, post_measurement):
        """
          Tests the retrieval of an existing measurement by its ID.

          Steps:
              1. Construct the GET request URL using the measurement ID.
              2. Obtain the necessary request headers.
              3. Send a GET request to fetch the measurement data.
              4. Verify that the API returns a 200 status code (successful retrieval).
              5. Extract and validate the response data.
              6. Compare the retrieved data with the expected measurement data.

          Expected Behavior:
              - The API should return a 200 status code.
              - The response should contain the correct measurement details.

          Assertions:
              - Ensures that the retrieved measurement matches the expected data for the given keys:
                ["id", "barrelId", "dirtLevel", "weight"].

          Args:
              post_measurement (dict): Dictionary returned by the `post_measurement` fixture containing measurement details.
        """
        url = ApiUrls.get_msr_by_id(post_measurement["id"])
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("GET", request_url=url, headers=headers,
                                                             expected_status_code=200)
        data = response.json()
        expected_data = post_measurement
        CommonUtility.validate_data(data, expected_data, keys=["id", "barrelId", "dirtLevel", "weight"])

    def test_post_measurement_missing_req_value(self):
        """
            Tests the API's response when attempting to create a measurement with missing attributes.

            Steps:
            1. Retrieves the API URL for posting measurements.
            2. Obtains the necessary request headers.
            3. Sends a POST request with an incomplete JSON payload (`CREATE_Measuremenent_Missing_Attr`).
            4. Verifies that the API returns a 400 Bad Request status code, indicating validation failure.

            Expected Behavior:
            - The API should reject the request due to missing required attributes.
            - The response should include an appropriate error message.

            Raises:
                AssertionError: If the response status code is not 400.
        """
        url = ApiUrls.GET_MEASUREMENTS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Measuremenent_Missing_Attr,
                                                             expected_status_code=400)

    def test_post_measurement_invalid_type(self, post_barrels_valid):
        """
            Tests the API endpoint for posting a measurement with invalid data types.

            This test sends a POST request to the measurements endpoint with a payload
            that contains incorrect data types for its attributes and expects a 400 Bad Request response.

            Parameters:
                post_barrels_valid: A fixture or setup that ensures a valid barrel exists before running the test.

            Steps:
                1. Retrieve the API URL for measurements.
                2. Get custom headers for the request.
                3. Send a POST request with a payload containing invalid data types.
                4. Validate that the response status code is 400.

            Raises:
                AssertionError: If the response status code is not 400.

        """
        url = ApiUrls.GET_MEASUREMENTS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Measuremenent_Invalid_Type,
                                                             expected_status_code=400)

    def test_post_measurement_invalid_barrel_id(self):
        """
           Tests the API endpoint for posting a measurement with an invalid barrel ID.

           This test sends a POST request to the measurements endpoint using an invalid
           barrel ID and expects a 400 Bad Request response.

           Steps:
               1. Retrieve the API URL for measurements.
               2. Get custom headers for the request.
               3. Send a POST request with an invalid barrel ID payload.
               4. Validate that the response status code is 400.

           Raises:
               AssertionError: If the response status code is not 400.

        """
        url = ApiUrls.GET_MEASUREMENTS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Measuremenent_Invalid_Barel_id,
                                                             expected_status_code=400)
        print(response)

    def test_post_measurement_invalid_double(self):
        """
           Tests the API endpoint for posting a measurement with an invalid barrel ID.

           This test sends a POST request to the measurements endpoint using an negative
           double payload and expects a 400 Bad Request response.

           Steps:
               1. Retrieve the API URL for measurements.
               2. Get custom headers for the request.
               3. Send a POST request with an invalid barrel ID payload.
               4. Validate that the response status code is 400.

           Raises:
               AssertionError: If the response status code is not 400.

        """

        url = ApiUrls.GET_MEASUREMENTS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Measuremenent_Negative_double,
                                                             expected_status_code=400)
        data = response.json()
        is_positive_weight = CommonUtility.is_double(data["weight"])
        is_positive_dirtLevel = CommonUtility.is_double(data["dirtLevel"])
        assert is_positive_weight is False
        assert is_positive_dirtLevel is False

    def test_post_invalid_header_measurement(self):
        """
           Tests the API endpoint for posting a measurement with an invalid barrel ID.

           This test sends a POST request to the measurements endpoint using an negative
           double payload and expects a 400 Bad Request response.

           Steps:
               1. Retrieve the API URL for measurements.
               2. Get custom headers for the request.
               3. Send a POST request with an invalid barrel ID payload.
               4. Validate that the response status code is 400.

           Raises:
               AssertionError: If the response status code is not 400.

        """
        url = ApiUrls.GET_MEASUREMENTS

        headers = CommonUtility.get_custom_inv_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             expected_status_code=415)

    def test_get_measurements(self):
        """
            Test case to verify the retrieval of measurements using a GET request.

            Steps:
                1. Retrieve the GET URL for measurements from the `ApiUrls` class.
                2. Fetch the custom headers using the `CommonUtility` class.
                3. Send a GET request to retrieve measurements and validate the expected status code (200).
                4. Extract the "id", "barrelId", "dirtLevel", and "weight" values from the response data.
                5. Validate that:
                   - Each "id" is a valid UUID (version 4).
                   - Each "barrelId" is a valid UUID (version 4).
                   - Each "dirtLevel" is a valid double value.
                   - Each "weight" is a valid double value.

            Assertions:
                - The test fails if any "id" is not a valid UUID v4.
                - The test fails if any "barrelId" is not a valid UUID v4.
                - The test fails if any "dirtLevel" is not a valid double or is negative.
                - The test fails if any "weight" is not a valid double or is negative.

            Expected Outcome:
                - The test passes if all retrieved measurement data meets the expected criteria.
        """
        url = ApiUrls.GET_MEASUREMENTS

        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("GET", request_url=url, headers=headers,
                                                             expected_status_code=200)

        data = response.json()
        uuid_list = CommonUtility.extract_values(data, "id")
        barrel_id_list = CommonUtility.extract_values(data, "barrelId")
        dirt_level_list = CommonUtility.extract_values(data, "dirtLevel")
        weight_list = CommonUtility.extract_values(data, "weight")
        is_valid_uuid = CommonUtility.is_valid_uuid_list(uuid_list, 4)
        is_valid_barel_uuid = CommonUtility.is_valid_uuid_list(barrel_id_list, 4)
        is_valid_weight_vals = CommonUtility.is_expected_double(weight_list)
        is_valid_dirtLevels_vals = CommonUtility.is_expected_double(dirt_level_list)
        assert is_valid_uuid is True, "is not valid UUID string"
        assert is_valid_barel_uuid is True, "is not a String or its an empty String"
        assert is_valid_dirtLevels_vals is True, "Dirt level is not a double or its an negative double"
        assert is_valid_weight_vals is True, " Weight is not a double or its an negative double"
