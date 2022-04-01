"""Utility function to help create Airtable requests"""

from typing import List, Union, Tuple
from urllib.parse import quote

FILTER_ARG = "filterByFormula"


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


if __name__ == "__main__":
    print(multiple_exact_value_filter(("payer_name", "BCBSTX"), ("network_status", "INN")))
