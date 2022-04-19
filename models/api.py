"""Holds the models for interacting with the Airtable API"""
from dataclasses import dataclass
from typing import List


@dataclass(order=True)
class Base:
    @classmethod
    def from_api(cls, data: dict):
        """data from the api comes in the form
        {
           "id": "ASDFDSAFSDJH",
           "fields": {
               "other": "thing"
           }
        }

        Requires a special constructor for the dataclass    

        Args:
            data (dict): raw API response

        Returns:
            Object Instance
        """
        # catch the API errors
        try:
            return cls(data.get("id"), **data.pop("fields"))
        except KeyError as e:
            print(data)
            raise e

    @staticmethod
    def custom_factory(data):
        def convert_value(obj):
            if isinstance(obj, list):
                return ", ".join(obj)
            return obj

        return dict((k, convert_value(v)) for k, v in data)


@dataclass
class Insurance(Base):
    id: str
    insurance_name: str
    payer_name: str
    financial_class: str = None
    network_status: str = None
    referral_required: str = None
    plan_type: str = None
    time_requested: int = 0


@dataclass
class CPT_code(Base):
    id: str = None
    name: str = None
    code: int = None
    trade_names: List[str] = None
    description: str = None
    abbreviation: str = None
    age_minimum: int = 0
    age_maximum: int = 1000
    financial_class_exceptions: List[str] = None
    coverage_exceptions: List[str] = None
    AuthorizationRequired: bool = False


@dataclass
class Provider(Base):

    id: str
    NPI: int
    Provider: str
    Location: str
    Specialty: str

    def __str__(self) -> str:
        last, first = self.Provider.split(", ")
        return f"{first.capitalize()} {last.capitalize()}"
