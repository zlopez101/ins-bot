from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List
from urllib.parse import quote

from enum import Enum


class PlanType(Enum):

    HMO_SNP = "HMO-SNP"
    HMO_D_SNP = "HMO D-SNP"
    PPO = "PPO"
    EPO = "EPO"
    HMO = "HMO"
    POS = "POS"
    MMP = "MMP"


class FinancialClass(Enum):

    MEDICARE = "Medicare"
    MEDICAID = "Medicaid"
    COMMERCIAL = "Commercial"


class NetworkStatus(Enum):

    INN = "INN"
    OON = "OON"
    NON = "NON"


@dataclass
class ConversationData:

    payer_name: str = None
    coverage_name: str = None
    cpt_code: int = None


@dataclass
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
            Insurance Instance
        """
        assert isinstance(data["fields"]["payer_name"], str), f"{data}"
        return cls(data.get("id"), **data.pop("fields"))

    @staticmethod
    def custom_factory(data):
        def convert_value(obj):
            if isinstance(obj, list):
                return ", ".join(obj)
            return obj

        return dict((k, convert_value(v)) for k, v in data)

    def __call__(self) -> dict:
        return asdict(self, dict_factory=self.custom_factory)


@dataclass
class Insurance(Base):
    pass


@dataclass
class CPT_code(Base):
    name: str
    code: int
    trade_names: List[str]
    description: str
    abbreviation: str
    age_minimum: int = 0
    age_maximum: int = 1000


@dataclass
class Insurance(Base):

    id: str
    insurance_name: str
    payer_name: str
    financial_class: FinancialClass
    network_status: NetworkStatus
    referral_required: str
    plan_type: PlanType = None


@dataclass
class Payer(Base):

    payer_name: str


@dataclass
class InsuranceFromAPI(Insurance):
    @classmethod
    def from_api(cls, data):
        return cls(**data["fields"])  # , id=data["id"])


class EncodedParameter:
    def __init__(self, s: str):
        self.s = quote(s)

    def __str__(self) -> str:
        return self.s
