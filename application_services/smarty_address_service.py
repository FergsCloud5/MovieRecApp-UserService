from smartystreets_python_sdk import StaticCredentials, exceptions, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup as StreetLookup

import os
import logging

from application_services.base_address_service import BaseAddressService


class SmartyAddressService(BaseAddressService):

    def __init__(self):
        pass

    @classmethod
    def get_api_keys(cls):
        auth_id = os.environ['SMARTY_AUTH_ID']
        auth_token = os.environ['SMARTY_AUTH_TOKEN']

        return auth_id, auth_token

    @classmethod
    def get_credentials(cls):
        auth_id, auth_token = cls.get_api_keys()
        credentials = StaticCredentials(auth_id, auth_token)

        return credentials

    @classmethod
    def lookup(cls, address_dto):
        creds = cls.get_credentials()

        client = ClientBuilder(creds).with_licenses(["us-core-cloud"]).build_us_street_api_client()

        lookup = StreetLookup()
        lookup.street = (str(address_dto.street_no) + " " + address_dto.street_name)
        lookup.city = address_dto.city
        lookup.state = address_dto.state
        lookup.zipcode = address_dto.zipcode
        lookup.candidates = 3

        try:
            client.send_lookup(lookup)
        except exceptions.SmartyException as err:
            logging.info(err)
            cls.candidates = None
            return

        cls.candidates = lookup.result

        if not cls.candidates:
            logging.info("No candidates. This means the address is not valid.")
            return

        return cls.candidates[0]
