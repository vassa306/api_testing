from utils.common_utils import CommonUtility


class Barrels:
    """
        A class that defines various test payloads and schemas for barrel and measurement entities.

        Attributes:
            CREATE_Barrel (dict): A valid payload for creating a barrel.
            CREATE_Barrel_Short_Values (dict): A payload with short values for barrel attributes.
            CREATE_Barrel_Missing_Values (dict): A payload missing required barrel attributes.
            CREATE_Barrel_Wrong_UUID (dict): A payload with an invalid UUID format.
            CREATE_Barrel_Invalid_Type (dict): A payload with incorrect data types for attributes.

            CREATE_Measuremenent_Valid (dict): A valid payload for creating a measurement.
            CREATE_Measuremenent_Missing_Attr (dict): A payload missing required measurement attributes.
            CREATE_Measuremenent_Invalid_Type (dict): A payload with incorrect data types for measurement attributes.
            CREATE_Measuremenent_Invalid_Barel_id (dict): A payload with an invalid barrel ID format.
            CREATE_Measuremenent_Negative_double (dict): A payload with negative values for dirt level and weight.

            Barrels_Schema (dict): The JSON schema defining the structure of a barrel.
            Measurement_Schema (dict): The JSON schema defining the structure of a measurement.
    """

    random_uuid = CommonUtility.generate_random_uuid()

    CREATE_Barrel = {
        "id": random_uuid,
        "qr": "aaaaaaaaa",
        "rfid": "ccccccc",
        "nfc": "bbbbbbbb"
    }

    CREATE_Barrel_Boundary_Values = {
        "id": random_uuid,
        "qr": "",
        "rfid": "ccccccc",
        "nfc": "bbbbbbbb"
    }

    CREATE_Barrel_Missing_Values = {
        "id": random_uuid,
        "qr": "ddd",
        "nfc": "bbbbbbbb"
    }

    CREATE_Barrel_Wrong_UUID = {
        "id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "qr": "a",
        "rfid" "d"
        "nfc": "b"
    }

    CREATE_Barrel_Invalid_Type = {
        "id": random_uuid,
        "gr": 2,
        "rfid": 3,
        "nfc": "test_nfc_v"
    }

    CREATE_Measuremenent_Valid = {
        "id": random_uuid,
        "barrelId": CREATE_Barrel["id"],
        "dirtLevel": 1.0,
        "weight": 20.0
    }

    CREATE_Measuremenent_Missing_Attr = {
        "id": random_uuid,
        "barrelId": CREATE_Barrel["id"],
        "dirtLevel": 1.0,
    }

    CREATE_Measuremenent_Invalid_Type = {
        "id": 12,
        "barrelId": CREATE_Barrel["id"],
        "dirtLevel": 1,
        "weight": "aaaa"
    }

    CREATE_Measuremenent_Valid_MSGS = {
        "id": random_uuid,
        "barrelId": "",
        "dirtLevel": 0.0,
        "weight": 0.0,
    }

    CREATE_Measuremenent_Invalid_Barel_id = {
        "id": random_uuid,
        "barrelId": 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        "dirtLevel": 1.0,
        "weight": 10.0
    }

    CREATE_Measuremenent_Negative_double = {
        "id": random_uuid,
        "barrelId": CREATE_Barrel["id"],
        "dirtLevel": -1.0,
        "weight": -10.0
    }

    Barrels_Schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "qr": {"type": "string", "minLength": 1},
            "rfid": {"type": "string", "minLength": 1},
            "nfc": {"type": "string", "minLength": 1}
        },
        "required": ["qr", "rfid", "nfc"]
    }

    Measurement_Schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "barrelId": {"type": "string", "format": "uuid"},
            "dirtLevel": {"type": "number"},
            "weight": {"type": "number"}
        },
        "required": ["barrelId", "dirtLevel", "weight"]
    }

    # ######### validation msgs ############################################

    expected_errors = {
        "qr": ["The Qr fiels is required"],
        "rfid": ['The Rfid field is required.'],
        "nfc": ['The Nfc field is required.'],
        "barrelId": ["The barrel field is required."],
        "dirtLevel": ["The dirtLevel field is required."],
        "weight": ["The weight field is required."],
        "$.barrelId": ["invalid uuid value"],
        "$.id": ["invalid uuid value"]
    }

    expected_errors_invalid = {
        "qr": ["qr must be string"],
        "rfid": ['rfid must be string']
    }

    expected_errors_titles = {
        "title_media": "Unsupported Media Type"
    }

