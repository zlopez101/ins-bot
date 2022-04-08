"""This module provides the utilities (functions, and constants) for interacting with Airtable API"""


from aiohttp import ClientSession
import os
from typing import List, Union
from urllib.parse import quote
from enum import Enum

if os.environ.get("production"):
    from dotenv import load_dotenv

    load_dotenv()

HEADERS = {
    "Authorization": f"Bearer {os.environ['API_key']}",
    "Content-Type": "application/json",
}


class URL(Enum):
    INS_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['insurance_table_id']}"
    CPT_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['cpt_codes_table_id']}"
    FC_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['fc_table_id']}"
    PROVIDER_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['providers_table_id']}"


FILTER_ARG = "filterByFormula"


class Session:
    def __init__(self):
        self.headers = HEADERS

    async def __aenter__(self) -> ClientSession:
        if not hasattr(self, "session"):
            self.session = ClientSession(headers=self.headers)
        return self.session

    async def __aexit__(self, _not, sure, why):
        await self.session.close()
        del self.session


def exact_value_filter(field: str, value: str, asdict=True) -> Union[dict, str]:
    """Airtable has a specific filterbyformula specification.
    This helper function creates the proper string

    Args:
        field (str): field to filter by
        value (str): the value to filter to

    Returns:
        str: formatted string
    """
    if asdict:
        return {FILTER_ARG: f'({{{field}}} = "{value}")'}
    else:
        return f'{FILTER_ARG}=({{{field}}} = "{value}")'


def multiple_exact_value_filter(*args) -> dict:
    """Airtable has a specific filterbyformula specification.
    This helper function creates the proper string

    Args:
        filters (List[Tuple[str, str]]): field (str): field to filter by
                                         value (str): the value to filter to

    Returns:
        dict: _description_
    """
    filters = []
    for arg in args:
        temp = exact_value_filter(arg[0], arg[1])
        filters.append(temp[FILTER_ARG])
    return {FILTER_ARG: f'AND({", ".join(filters)})'}


def filter_unique(field: str, asdict=True) -> Union[dict, str]:
    if asdict:
        pass
    else:
        return f"{FILTER_ARG}=(ARRAYUNIQUE({{{field}}}))"


def string_contains_field_filter(field: str, value: str) -> dict:
    """TBD

    Args:
        field (str): _description_
        value (str): _description_

    Returns:
        dict: _description_
    """
    pass


def process_dict(dct: dict) -> str:
    """"""
    result = "?"
    for key, value in dct.items():
        result += f"&{quote(key)}={quote(value)}"

    return result


def select_fields(field: List[str]) -> str:
    """Must be used on the

    Args:
        field (List[str]): _description_

    Returns:
        str: _description_
    """
    if isinstance(field, list):
        # list
        res = "&".join([f"fields[]={f}" for f in field])
    else:
        # string
        res = f"fields[]={field}"
    return quote(res, safe="=")
