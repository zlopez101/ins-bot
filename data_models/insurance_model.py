# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Union
from botbuilder.schema import Attachment

# from .db_connection import AzureDB
import json


def get_cpt_code_references(user_input: Union[str, int]) -> dict:
    """Will accept user input and bring back relevant info for the cpt code

    Args:
        user_input (Union[str, int]): [description]

    Returns:
        dict: [description]
    """


def perform_insurance_cpt_check(cpt_code: str, insurance: str) -> dict:
    """Check whether the cpt_code is covered by the insurance

    Args:
        cpt_code (str): Code to check
        insurance (str): Insurance to check against

    Returns:
        dict: dictionary containing the code, covered? result, insurance, and optional explanation
    """
    res = True
    return {
        "code": cpt_code,
        "covered?": "covered" if res else "not covered",
        "insurance": insurance,
    }


class VaccineToCPTCode:
    """if user provides the name of the vaccine -> convert to CPT code
    """

    def __init__(self, vaccineName: str):
        self.vaccineName = vaccineName

    def get_aliases() -> list:
        pass


class UserProfile:
    """
      This is our application state. Just a regular serializable Python class.
    """

    def __init__(
        self,
        insurance: str = None,
        vaccine: str = None,
        age: int = 0,
        picture: Attachment = None,
    ):
        self.insurance = insurance
        self.vaccine = vaccine
        self.age = age
        self.picture = picture
