from enum import Enum
from ..config import Config


class RelevanceFilters(Enum):
    RELEVANT = 'R'
    RECENT = 'DD'


class TimeFilters(Enum):
    ANY = ''
    DAY = 'r86400'
    WEEK = 'r604800'
    MONTH = 'r2592000'


class TypeFilters(Enum):
    FULL_TIME = 'F'
    PART_TIME = 'P'
    TEMPORARY = 'T'
    CONTRACT = 'C'
    INTERNSHIP = 'I'
    VOLUNTEER = 'V'
    OTHER = 'O'


class ExperienceLevelFilters(Enum):
    def __init__(self, value):
        super().__init__(value)
    def __str__(self):
        return self.key
    INTERNSHIP = '1'
    ENTRY_LEVEL = '2'
    ASSOCIATE = '3'
    MID_SENIOR = '4'
    DIRECTOR = '5'
    EXECUTIVE = '6'


class OnSiteOrRemoteFilters(Enum):
    ON_SITE = '1'
    REMOTE = '2'
    HYBRID = '3'


class IndustryFilters(Enum):
    def __init__(self, value):
        super().__init__(value)
    ACCOMMODATION_SERVICES = '2190'
    ADMINISTRATIVE_AND_SUPPOR_SERVICES = '1912'
    CONSTRUCTION = '48'
    CONSUMER_SERVICES = '91'
    EDUCATION = '1999'
    ENTERTAINMENT_PROVIDERS = '28'
    FARMING_RANCHING_FORESTRY = '201'
    FINANCIAL_SERVICES = '43'
    GOVERNMENT_ADMINISTRATION = '75'
    HOSPITALS_AND_HEALTH_CARE = '14'
    MANUFACTURING = '25'
    PROFESSIONAL_SERVICES = '96'
    REAL_ESTATE_AND_EQUIPMENT_RENTAL_SERVICES = '1757'
    RETAIL = '27'
    TECHNOLOGY_INFORMATION_AND_MEDIA = '4'

    def getValueFromKey(key):
        return IndustryFilters[key].value
