from application_services.BaseApplicationResource import BaseApplicationResource
from database_services.RDBService import RDBService
from application_services.smarty_address_service import SmartyAddressService
from application_services.base_address_service import AddressDataTransferObject
import sys
import logging


class addressResource(BaseApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data):
        for r in resource_data:
            address_id = r.get('addressID')
            user_id = r.get('userID')

            links = []
            self_link = {"rel": "self", "href": "/addresses/" + str(address_id)}
            links.append(self_link)

            r["links"] = links
        return resource_data

    @classmethod
    def get_all_addresses(cls):
        return RDBService.get_resource("user_service", "address")

    @classmethod
    def get_address_by_id(cls, id):
        return RDBService.find_by_template("user_service", "address",
                                           {"addressID": id})

    @classmethod
    def get_user_by_address(cls, id):
        return RDBService.find_by_template("user_service", "user",
                                           {'addressID': id})

    @classmethod
    def add_address(cls, address):
        if not address:
            return None
        smarty = SmartyAddressService()
        address_dto = AddressDataTransferObject(address)
        smarty_address = smarty.lookup(address_dto)
        if smarty_address:
            # TODO: put smarty_address into db
            return RDBService.create("user_service", "address", address)
        else:
            return None

    @classmethod
    def update_address(cls, id, update_data):
        return RDBService.update("user_service", "address", update_data, id)

    @classmethod
    def delete_address(cls, id):
        return RDBService.delete_resource("user_service", "address", id)
