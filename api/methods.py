"""This module provides the base methods for interacting the Airtable API"""

from typing import Dict, Tuple
from aiohttp import ClientProxyConnectionError, ClientSession, ClientResponse


async def _raise_for_status(
    response: ClientResponse, response_object
) -> Tuple[dict, str]:

    response.raise_for_status()
    resp: dict = await response.json()
    offset = resp.pop("offset", "")
    records = resp.pop("records")
    # if retrieving a single record, the response object doesn't contain `key` "records"
    if records:
        res = sorted([response_object.from_api(record) for record in records])
    else:
        # note: uses `resp` not `records`
        res = response_object.from_api(resp)
    return res, offset


async def _list_records(
    session: ClientSession,
    url: str,
    response_object: object,
    params: dict = None,
    pageSize: int = 5,
    offset: str = None,
):
    if params:
        # only update params with key,value pairs that have a value
        params.update(
            {k: v for k, v in zip(["pageSize", "offset"], [pageSize, offset]) if v}
        )
    async with session.get(url, params=params) as resp:
        return await _raise_for_status(resp, response_object)


async def _retrieve_record(
    session: ClientSession, url: str, id: str, response_object: object
):
    async with session.get(url + id) as resp:
        return await _raise_for_status(resp, response_object)


async def _patch_record(
    session: ClientSession, url: str, id: str, updates: Dict[str, str]
):
    """Update the airtable API record corresponding to ID with updates dict

    Args:
        session (ClientSession): 
        url (str): URL corresponding to table where id lives    
        id (str): id of object to update
        updates (Dict[str, str]): updates with keys as field names, values as new values
    """
    data = dict(records=[dict(id=id, fields=updates)])
    async with session.patch(url, json=data) as resp:
        return await resp.json()


async def _create_record(session: ClientSession, url: str, data):
    pass
