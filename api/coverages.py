"""Implements all the necessary insurance coverage calls to the Airtable API"""

from typing import List, Tuple
from aiohttp import ClientSession, ClientResponse
from models.api import Insurance, CPT_code, Provider
from .utils import exact_value_filter, select_fields, filter_unique, multiple_exact_value_filter, URL, HEADERS
from .methods import _raise_for_status, _list_records, _retrieve_record


async def get_payers(session: ClientSession) -> List[str]:
    """Get the payer names. This method won"""
    coverages, _ = await _list_records(session, URL.INS_URL.value, Insurance)
    return list(set([coverage.payer_name for coverage in coverages]))

async def get_coverages_by_payer_name(
    session: ClientSession, payerName: str, inn_only: bool=True, pageSize: int = 5, offset: str = None
) -> Tuple[List[Insurance], str] :
    """Return the coverages associated with the payer name

    Args:
        session (ClientSession): session 
        payerName (str): payer name to filter on. Selected from get_payers
        inn_only (bool, optional): In-network coverages only. Defaults to True.
        pageSize (int, optional): The page size to query. Defaults to 5.
        offset (str, optional): Used to filter to the next page. Defaults to None.

    Returns:
        List[Insurance]: coverages to be displayed for selection
    """
    
    # build the parameters dictionary
    if inn_only:
        params = multiple_exact_value_filter(("payer_name", payerName), ("network_status", "INN"))
    else:
        params = exact_value_filter("payer_name", payerName)
    
    print(URL.INS_URL.value)
    print(params)

    return await _list_records(session, URL.INS_URL.value, Insurance, params=params, pageSize=pageSize, offset=offset)
       

async def get_coverage_by_id(session: ClientSession, id: str) -> Insurance:
    return _retrieve_record(session, URL.INS_URL.value, id, Insurance)


async def get_coverage_by_name(session: ClientSession, name: str) -> Insurance:
    return await _list_records(session, URL.INS_URL.value, Insurance, params=exact_value_filter("insurance_name", name))\


async def get_financial_classes_by_name(session: ClientSession, name: str) -> dict:
    """TBD"""
    pass
    # async with session.get(URL.FC_URL.value, params=exact_value_filter('name', name)) as resp:
    # r

async def get_locations(session: ClientSession) -> List[str]:
    """Get the CBC locations

    Args:
        session (ClientSession): session to use
        
    Returns:
        List[str]: List of locations
    """
    async with session.get(URL.PROVIDER_URL.value) as resp:
        results = await resp.json()
        records = results['records']
        return list(set([record['fields']['Location'] for record in records]))

async def get_providers_at_location(session: ClientSession, location: str) -> List[Provider]:
    async with session.get(URL.PROVIDER_URL.value, params=exact_value_filter('Location', location)) as resp:
        return await _raise_for_status(resp, Provider)

