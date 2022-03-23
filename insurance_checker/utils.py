from urllib.parse import quote

FILTER_ARG = "filterByFormula"

def field_filter(field: str, value: str) -> dict:
    """Airtable has a specific filterbyformula specification.
    This helper function creates the proper string

    Args:
        field (str): field to filter by
        value (str): the value to filter to

    Returns:
        str: formatted string
    """
    return {FILTER_ARG: f'({{{field}}} = "{value}")'}