"""Implements all the cpt_code calls to the Airtable API"""

from aiohttp import ClientSession
from models.api import CPT_code
from .methods import _list_records, _raise_for_status, _retrieve_record
from .utils import exact_value_filter, URL
from typing import List



async def get_code_by_id(session: ClientSession, id: str) -> CPT_code:
    async with session.get(URL.CPT_URL.value + "/" + id) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_code_by_code(session: ClientSession, code: str) -> CPT_code:
    async with session.get(URL.CPT_URL.value, params=exact_value_filter("code", code)) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_code_by_exact_name(session: ClientSession, name: str) -> CPT_code:
    async with session.get(URL.CPT_URL.value, params=exact_value_filter("name", name)) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_code_by_name_includes(session: ClientSession, name: str) -> CPT_code:
    async with session.get(URL.CPT_URL.value, params=exact_value_filter("name", name)) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_codes_by_type(session: ClientSession, type=str) -> List[CPT_code]:
    """TBD"""
    pass