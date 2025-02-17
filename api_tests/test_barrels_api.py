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
    def post_barrel_valid(self):
        """
            Test case to create a new barrel via API and validate its creation.

            This test performs the following steps:

            1. **Create a barrel**:
               - Sends a `POST` request to the `GET_BARRELS` API endpoint with the necessary payload.
               - Verifies that the response status code is `201 Created`.
               - Extracts the `id`, `qr`, `rfid`, and `nfc` from the response.

            2. **Validate the response**:
               - Ensures the response conforms to the expected `JSON` schema.
               - Confirms that the `Content-Type` of the response is `application/json; charset=utf-8`.

            3. **Validate barrel existence**:
               - Retrieves the list of barrels with a `GET` request.
               - Asserts that the newly created barrel exists in the response data.

            Assertions:
            - The response structure must match the defined `Barrels_Schema`.
            - The `Content-Type` should be `application/json; charset=utf-8`.
            - The newly created barrel should be found in the subsequent `GET` request response.

            Yields:
            - The response data from the `POST` request to facilitate further validation.

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
    def test_post_barrel_invalid_headers(self):
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
    def test_delete_barrel(self, post_barrel_valid):
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

        url = ApiUrls.get_barrel_by_id(post_barrel_valid["id"])
        print(url)
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("DELETE", request_url=url, headers=headers,
                                                             expected_status_code=200)

        # call again get with the same value. should return 404 because barrel was deleted.
        url = ApiUrls.get_barrel_by_id(post_barrel_valid["id"])
        response = FrameworkUtils.fire_api_with_cust_headers("GET", request_url=url, headers=headers,
                                                             expected_status_code=404)

    @mark.barrels
    def test_delete_barrel_inv_header(self, post_barrel_valid):
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
               post_barrel_valid (dict): Dictionary returned by the `post_barrels_valid` fixture containing barrel details.
        """

        url = ApiUrls.get_barrel_by_id(post_barrel_valid["id"])
        print(url)
        headers = CommonUtility.get_custom_inv_header()
        response = FrameworkUtils.fire_api_with_cust_headers("DELETE", request_url=url, headers=headers,
                                                             expected_status_code=400)

    @mark.barrels
    def test_create_twice_the_same_barrel(self, post_barrel_valid):
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
              post_barrel_valid (dict): A dictionary containing the details of a previously created barrel.

          Raises:
              AssertionError: If the API does not return a `409` status code when trying to create a duplicate barrel.

        """
        url = ApiUrls.GET_BARRELS
        data = post_barrel_valid
        print(data)
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=data,
                                                             expected_status_code=409)
        print(response)

    @mark.barrels
    def test_delete_barrel_invalid_id(self):
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
    def test_post_barrel_missing_req_value(self):
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
    def test_post_barrel_invalid_uuid(self):
        """
            Test case for attempting to create a barrel with an invalid UUID.

            This test verifies that the API correctly rejects a POST request containing an invalid UUID
            and returns a 400 Bad Request response.

            **Test Steps:**
            1. Retrieve the API URL from `ApiUrls.GET_BARRELS`.
            2. Obtain custom headers using `CommonUtility.get_custom_header()`.
            3. Send a POST request to the API with an invalid UUID payload (`Barrels.CREATE_Barrel_Wrong_UUID`).
            4. Validate that the response status code is 400.
            5. Verify that the error message in the response matches the expected validation message.

            **Assertions:**
            - The response should have a status code of `400 Bad Request`, indicating a client-side validation failure.
            - The error message for the `id` field in the response should match the expected validation error.

        """
        url = ApiUrls.GET_BARRELS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Barrel_Wrong_UUID,
                                                             expected_status_code=400)
        data = response.json()
        errors = Barrels.expected_errors
        print(data)
        assert data["errors"].get("$.id") == errors["$.id"], "invalid validation msg for barrel id"

    @mark.barrels
    def test_post_barrel_empty_body(self):
        """

        Test case to validate API behavior when attempting to create a barrel with an empty request body.

            **Test Objective:**
            - This test sends a `POST` request to the `GET_BARRELS` API endpoint with an **empty payload** `{}`.
            - It verifies that the API correctly rejects the request with a `400 Bad Request` response.
            - Ensures that the error messages correctly match the expected validation messages.

            **Test Steps:**
            1. Retrieve the API URL from `ApiUrls.GET_BARRELS`.
            2. Obtain custom headers using `CommonUtility.get_custom_header()`.
            3. Send a `POST` request with an **empty JSON body** `{}`.
            4. Validate that the response returns a `400` status code.
            5. Verify that the error messages correctly indicate missing required fields (`qr`, `nfc`, `rfid`).

            **Assertions:**
            - The API must return a `400 Bad Request` status.
            - The `"errors"` field in the response must contain the expected validation messages.
            - Error messages must match the **expected field names** and validation responses.

            **Raises:**
            - `AssertionError`: If the API response does not match expected validation messages.
        """

        url = ApiUrls.GET_BARRELS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json={},
                                                             expected_status_code=400)
        expected_errors = Barrels.expected_errors
        data = response.json()
        # error because attributes from api does not match attrs in swagger e.g. Qr, Nfc, Rfid
        assert data["errors"].get("qr") == expected_errors["qr"], "invalid name of attribute  in json or invalid " \
                                                                  "message"
        assert data["errors"].get("nfc") == expected_errors[
            "nfc"], "invalid name of attribute in in json or invalid message"
        assert data["errors"].get("rfid") == expected_errors["rfid"], "invalid name of attribute in json or invalid msg"

    @mark.barrels
    def test_post_barrel_invalid_param_type(self):
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
        data = response.json()
        expected_errors = Barrels.expected_errors_invalid
        actual = data["errors"].get('rfid')
        # also return nonsense instead of The barrel field is required, should be qr has invalid format
        assert actual == expected_errors['rfid'], f"validation message was {actual} for rfid"

    @mark.barrels
    def test_response_time_get_barrels(self):
        """
            Measures the response time of the GET request to fetch barrels and ensures it is within the acceptable threshold.

            Steps:
            1. Retrieves the API URL for fetching barrels.
            2. Obtains the necessary headers.
            3. Records the start time of the request.
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
    def post_measurement(self, post_barrel_valid):
        """
            Sends a POST request to create a measurement for a given barrel and validates the response.

            Args:
                post_barrel_valid (str): The ID of the barrel for which the measurement is being posted.

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
              post_measurement (dict): Dictionary returned by the `post_measurement` fixture containing
              measurement details.
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
             Test API response when attempting to create a measurement with missing required attributes.

             **Test Steps:**
             1. Retrieve the API endpoint URL for posting measurements.
             2. Obtain the necessary request headers.
             3. Send a `POST` request with an incomplete JSON payload (`CREATE_Measurement_Missing_Attr`).
             4. Verify that the API returns a `400 Bad Request` status code, indicating validation failure.
             5. Validate that the response contains an appropriate error message for the missing `weight` field.

             **Expected Behavior:**
             - The API should reject the request due to missing required attributes.
             - The response should contain an `"errors"` object specifying that `weight` is a required field.

             **Assertions:** - The response status code must be `400`. - The `errors` key in the response must
             include an error message for `weight`, matching the expected validation message.

             **Raises:** - `AssertionError`: If the response status code is not `400` or the validation message for
             `weight` is incorrect.
        """
        url = ApiUrls.GET_MEASUREMENTS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Measuremenent_Missing_Attr,
                                                             expected_status_code=400)
        data = response.json()
        expected_error = Barrels.expected_errors
        print(data)
        # should be weight but message is for barrel
        assert data["errors"].get("weight") == expected_error['weight'], "invalid validation message for weight"

    def test_post_measurement_validation_msgs(self):
        """
                Tests the API endpoint for posting a measurement with invalid data types and missing required fields.

                This test verifies that the API correctly validates incoming measurement data and returns appropriate
                error messages when invalid data types are used or required fields are missing.

            Test Steps:
                1. Retrieve the API URL for measurements from `ApiUrls.GET_MEASUREMENTS`.
                2. Get custom headers using `CommonUtility.get_custom_header()`.
                3. Send a POST request to the API with a payload (`Barrels.CREATE_Measuremenent_Valid_MSGS`) that contains:
                   - Invalid data types.
                   - Missing required fields.
                4. Validate that the response returns a **400 Bad Request** status.
                5. Extract and verify the validation error messages in the response.

            Assertions:
                - The response should contain an `"errors"` key.
                - The `"title"` in the response should be `'One or more validation errors occurred.'`.
                - The validation message for `barrelId` should match the expected error from `Barrels.expected_errors["barrelId"]`.
                - The validation message for `dirtLevel` should confirm that the field is required.
                - The validation message for `weight` should confirm that the field is required.

            Raises:
                AssertionError: If any of the validation conditions fail.
        """
        url = ApiUrls.GET_MEASUREMENTS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Measuremenent_Valid_MSGS,
                                                             expected_status_code=400)
        expected_errors = Barrels.expected_errors
        response_json = response.json()
        error = response_json['errors']
        title = response_json["title"]
        barrel_id = response_json["errors"].get("barrelId")
        # dirt level msg missing but its required field
        dirt_level = response_json["errors"].get("dirtLevel")
        weight = response_json["errors"].get("weight")

        print(error)
        print("id messsage is ", id)

        exp_title = 'One or more validation errors occurred.'
        assert "errors" in response_json, "Response does not contain 'errors' key"
        assert exp_title == title, "response does not contain validation message title"
        assert barrel_id == expected_errors["barrelId"], "response does not have proper validation message for " \
                                                         "barrelId," \
                                                         " is required filed"
        assert dirt_level == expected_errors["dirtLevel"], "API response does not contain the expected validation " \
                                                           "message for 'dirtLevel'. " \
                                                           "The 'dirtLevel' field is required."
        assert weight == expected_errors["weight"], "API response does not contain the expected validation " \
                                                    "message for 'weight'. " \
                                                    "The 'weight' field is required."

    def test_post_measurement_invalid_barrel_id(self):
        """
            Tests the API endpoint for posting a measurement with an invalid barrel ID.

            This test verifies that the API correctly validates the `barrelId` field and returns
            an appropriate error message when an invalid value (e.g., an incorrect UUID format)
            is provided.

            Test Steps:
                1. Retrieve the API URL for measurements from `ApiUrls.GET_MEASUREMENTS`.
                2. Obtain valid custom headers using `CommonUtility.get_custom_header()`.
                3. Send a POST request with an **invalid `barrelId`** payload
                   (`Barrels.CREATE_Measuremenent_Invalid_Barel_id`).
                4. Validate that the response returns a **400 Bad Request** status.
                5. Extract and verify the validation error message for `barrelId`.

            Assertions:
                - The response should have a status code of `400 Bad Request`.
                - The `"errors"` key in the response should contain a validation message for `$.barrelId`.
                - The validation message for `$.barrelId` should match the expected error from
                  `Barrels.expected_errors["$.barrelId"]`.

            Raises:
                AssertionError: If any of the validation conditions fail.
        """
        url = ApiUrls.GET_MEASUREMENTS
        headers = CommonUtility.get_custom_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             request_json=Barrels.CREATE_Measuremenent_Invalid_Barel_id,
                                                             expected_status_code=400)
        expected_error = Barrels.expected_errors
        data = response.json()

        assert data["errors"]["$.barrelId"] == expected_error["$.barrelId"], "invalid uuid message"

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
        print(data)
        is_positive_weight = CommonUtility.is_double(data.get("weight"))
        is_positive_dirtLevel = CommonUtility.is_double(data.get("dirtLevel"))
        assert is_positive_weight is False
        assert is_positive_dirtLevel is False

    def test_post_invalid_header_measurement(self):
        """
            Tests the API endpoint for posting a measurement with an invalid request header.
            This test verifies that the API correctly rejects requests with an invalid header format
            by returning a **415 Unsupported Media Type** response.

            Test Steps:
                1. Retrieve the API URL for measurements from `ApiUrls.GET_MEASUREMENTS`.
                2. Obtain **invalid** custom headers using `CommonUtility.get_custom_inv_header()`.
                3. Send a POST request to the API **without a valid `Content-Type` header**.
                4. Validate that the response returns a **415 Unsupported Media Type** status.
                5. Extract and verify the error message in the response.

            Assertions:
                - The response should have a status code of `415 Unsupported Media Type`.
                - The `"title"` in the response should match `Barrels.expected_errors_titles["title_media"]`.

            Raises:
                AssertionError: If any of the validation conditions fail.
        """
        url = ApiUrls.GET_MEASUREMENTS

        headers = CommonUtility.get_custom_inv_header()
        response = FrameworkUtils.fire_api_with_cust_headers("POST", request_url=url, headers=headers,
                                                             expected_status_code=415)
        data = response.json()
        expected_error = Barrels.expected_errors_titles
        print(data)
        assert data["title"] == expected_error["title_media"], "invalid header format validation msg"

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
        assert not data, "JSON response is not empty!"

