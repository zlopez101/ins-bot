"""Make Asynchronous API calls to the Airtable API
"""
from typing import List
from aiohttp import ClientSession, ClientResponse
from .models import Insurance, CPT_code, Provider
from .utils import (
    exact_value_filter,
    select_fields,
    filter_unique,
    multiple_exact_value_filter,
)

from dotenv import load_dotenv
from enum import Enum
import os

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


INS_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['insurance_table_id']}"
CPT_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['cpt_codes_table_id']}"
FC_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['fc_table_id']}"
PROVIDER_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['providers_table_id']}"


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


async def _raise_for_status(response: ClientResponse, response_object):

    response.raise_for_status()
    resp: dict = await response.json()
    offset = resp.pop("offset", "")
    records = resp.pop("records", {})
    # if retrieving a single record, the response object doesn't contain `key` "records"
    if records:
        res = [response_object.from_api(record) for record in records]
    else:
        res = response_object.from_api(resp)
    return res, offset


async def _list_records(session: ClientSession, url: URL, params: str = None):

    async with session.get(url):
        pass


async def _retrieve_record(session: ClientSession, url: URL, id: str):
    pass


async def _create_record(session: ClientSession, url: URL, data):
    pass


async def get_payers(session: ClientSession) -> list:
    params = (
        select_fields("payer_name") + "&" + filter_unique("payer_name", asdict=False)
    )
    async with session.get(INS_URL + "?" + params) as resp:
        res = await resp.json()
        records = res["records"]
        return list(set(record["fields"]["payer_name"] for record in records))


async def get_coverages_by_payer_name(
    session: ClientSession,
    payerName: str,
    inn_only: bool = True,
    pageSize: int = 5,
    offset: str = None,
) -> List[Insurance]:

    params = dict(pageSize=pageSize)
    if offset:
        params["offset"] = offset

    if inn_only:
        params.update(
            multiple_exact_value_filter(
                ("payer_name", payerName), ("network_status", "INN")
            )
        )
    else:
        params.update(exact_value_filter("payer_name", payerName))

    async with session.get(INS_URL, params=params) as resp:
        return await _raise_for_status(resp, Insurance)


async def get_coverage_by_id(session: ClientSession, id: str) -> Insurance:
    async with session.get(INS_URL + "/" + id) as resp:
        return await _raise_for_status(resp, Insurance)


async def get_coverage_by_name(session: ClientSession, name: str) -> Insurance:
    # use insurance_name field id -> changes to insurance_name field likely
    async with session.get(
        INS_URL, params=exact_value_filter("insurance_name", name)
    ) as resp:
        return await _raise_for_status(resp, Insurance)


async def get_code_by_id(session: ClientSession, id: str) -> CPT_code:
    async with session.get(CPT_URL + "/" + id) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_code_by_code(session: ClientSession, code: str) -> CPT_code:
    async with session.get(CPT_URL, params=exact_value_filter("code", code)) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_code_by_exact_name(session: ClientSession, name: str) -> CPT_code:
    async with session.get(CPT_URL, params=exact_value_filter("name", name)) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_code_by_name_includes(session: ClientSession, name: str) -> CPT_code:
    async with session.get(CPT_URL, params=exact_value_filter("name", name)) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_codes_by_type(session: ClientSession, type=str) -> List[CPT_code]:
    """TBD"""
    pass


async def get_financial_classes_by_name(session: ClientSession, name: str) -> dict:
    """TBD"""
    pass
    # async with session.get(FC_URL, params=exact_value_filter('name', name)) as resp:
    # r


async def get_locations(session: ClientSession) -> List[str]:
    """Get the CBC locations

    Args:
        session (ClientSession): session to use
        
    Returns:
        List[str]: List of locations
    """
    async with session.get(PROVIDER_URL) as resp:
        results = await resp.json()
        records = results["records"]
        return list(set([record["fields"]["Location"] for record in records]))


async def get_providers_at_location(
    session: ClientSession, location: str
) -> List[Provider]:
    async with session.get(
        PROVIDER_URL, params=exact_value_filter("Location", location)
    ) as resp:
        return await _raise_for_status(resp, Provider)


if __name__ == "__main__":
    import asyncio
    from pprint import pprint

    async def main():

        async with ClientSession(headers=HEADERS) as session:
            page, offset = await get_coverages_by_payer_name(session, "BCBSTX")

            print(page[0])

            next_page, offset = await get_coverages_by_payer_name(
                session, "BCBSTX", offset=offset
            )

            print(next_page[0])

            assert page != next_page

    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )  # windows issue
    asyncio.run(main())
