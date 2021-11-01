from abc import ABC, abstractmethod

candidate_fields = [
    'city_name', 'default_city_name', 'delivery_point', 'delivery_point_check_digit', 'extra_secondary_designator',
    'extra_secondary_number', 'plus4_code', 'pmb_designator', 'pmb_number', 'primary_number', 'secondary_designator',
    'secondary_number', 'state_abbreviation', 'street_name', 'street_postdirection', 'street_predirection',
    'street_suffix', 'urbanization', 'zipcode'
]


class AddressDataTransferObject:

    def __init__(self, address):
        self.unique_id = None
        self.street_no = address['streetNo']
        self.street_name = address['streetName1']
        self.city = address['city']
        self.state = address['region']
        self.zipcode = address['postalCode']
        self.extras = None


class BaseAddressService(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def lookup(self, address_dto):
        pass
