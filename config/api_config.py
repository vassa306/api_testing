from api_tests.functional_param import FunctionalParam


class ApiUrls:
    """
        A class that defines API endpoint URLs for accessing barrels and measurements.

        Attributes:
            GET_BARRELS (str): The URL for retrieving all barrels.
            GET_MEASUREMENTS (str): The URL for retrieving all measurements.

        Methods:
            get_barrel_by_id(barrel_id: int) -> str:
                Returns the API endpoint for retrieving a specific barrel by its ID.
            get_msr_by_id(mesr_id: int) -> str:
                Returns the API endpoint for retrieving a specific measurement by its ID.
    """

    GET_BARRELS = FunctionalParam.get_base_end_point() + "/barrels/"
    GET_MEASUREMENTS = FunctionalParam.get_base_end_point() + "/measurements/"

    @staticmethod
    def get_barrel_by_id(barrel_id):
        return FunctionalParam.get_base_end_point() + f'/barrels/{barrel_id}'

    @staticmethod
    def get_msr_by_id(mesr_id):
        return FunctionalParam.get_base_end_point() + f'/barrels/{mesr_id}'
