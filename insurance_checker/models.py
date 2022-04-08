from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List
from urllib.parse import quote

from enum import Enum, auto


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

    
specialties = {
    "PRIMARY": "primary",
    "PEDIATRICS": "primary",
    "INTERNAL MEDICINE": "primary",
    "ENDOCRINOLOGY": "primary",
    "PSYCHOLOGY": "psych",
    "CARDIOLOGY": "primary",
    "GERIATRIC MEDICINE": "primary",
    "GASTROENTEROLOGY": "specialty",
    "SOCIAL SERVICES": "pysch",
    "BARIATRICS": "specialty",
    "RHEUMATOLOGY": "specialty",
    "PAIN MEDICINE": "specialty",
    "CARDIOTHORACIC SURGERY": "specialty",
    "INFECTIOUS DISEASES": "specialty",
    "PEDIATRIC UROLOGY": "specialty",
    "ONCOLOGY": "specialty",
    "GENERAL SURGERY": "specialty",
    "NEPHROLOGY": "specialty",
    "DERMATOLOGY": "specialty",
    "PULMONARY DISEASE": "specialty",
    "CHILD AND ADOLESCENT PSYCHIATRY": "psych",
    "ORTHOPAEDIC SURGERY": "specialty",
    "PEDIATRIC NEPHROLOGY": "specialty",
    "PEDIATRIC ENDOCRINOLOGY": "specialty",
}

class IsSpecialist(Enum):

    Primary = 0
    Specialist = 1
    Psych = 2


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
class Insurance(Base):

    id: str
    insurance_name: str
    payer_name: str
    financial_class: FinancialClass = None
    network_status: NetworkStatus = None
    referral_required: str = None
    plan_type: PlanType = None

    def __str__(self):
        return self.insurance_name

    


@dataclass
class Payer(Base):

    payer_name: str


@dataclass
class UserProfile:

    name: str = None
    role: str = None
    location: str = None

    def __bool__(self):
        """Used in the main dialog for confirming if the user has a profile"""
        return True if self.name else False


@dataclass
class CPT_Code_Verification_State:

    cpt_code: int = None
    insurance_submitted: str = None


@dataclass
class Get_Correct_Coverage_State:
    pass


@dataclass
class Referral_Required_State:
    pass


@dataclass
class Main_Dialog_State:

    cpt_code_verification_state: CPT_Code_Verification_State
    get_correct_coverage_state: Get_Correct_Coverage_State
    referral_required_state: Referral_Required_State


@dataclass
class Conversation_State:

    patient: int = None
    patient_age: int = None
    coverage: Insurance = None
    provider: int = None
    location: str = None
    cpt_code: List[int] = None
    payer: str = None
        

@dataclass
class Provider(Base):

    id: str
    NPI: int
    Provider: str
    Location: str
    Specialty: str

    def __str__(self) -> str:
        last, first = self.Provider.split(', ')
        return f"{first.capitalize()} {last.capitalize()}"


if __name__ == '__main__':
    print(IsSpecialist(1).name)