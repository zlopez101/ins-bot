"""Make Asynchronous API calls to the Airtable API
"""
from audioop import mul
from typing import List
from aiohttp import ClientSession, ClientResponse, ClientResponseError
from insurance_checker.models import Insurance, CPT_code
from insurance_checker.utils import exact_value_filter, select_fields, filter_unique, multiple_exact_value_filter
from dotenv import load_dotenv
import os

load_dotenv()

HEADERS = {
    "Authorization": f"Bearer {os.environ['API_key']}",
    "Content-Type": "application/json",
}
INS_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['insurance_table_id']}"
CPT_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['cpt_codes_table_id']}"
FC_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['fc_table_id']}"


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
        records = await response.json()
        # if retrieving a single record, the response object doesn't contain `key` "records"
        records = records["records"]
        if len(records) > 1:
            return [response_object.from_api(record) for record in records]
        elif len(records) == 1:
            return response_object.from_api(records[0])
        else:  # when using a filter the API will return a list of length 1 if there's only 1 value
            return None



async def get_payers(session: ClientSession) -> list:
    params = (
        select_fields("payer_name") + "&" + filter_unique("payer_name", asdict=False)
    )
    async with session.get(INS_URL + "?" + params) as resp:
        res = await resp.json()
        records = res["records"]
        return list(set(record["fields"]["payer_name"] for record in records))


async def get_coverages_by_payer_name(
    session: ClientSession, payerName: str, both_inn_and_oon: bool=True
) -> List[Insurance]:
    if both_inn_and_oon:
        async with session.get(
            INS_URL, params=exact_value_filter("payer_name", payerName)
        ) as resp:
            return await _raise_for_status(resp, Insurance)
    else:
        async with session.get(
            INS_URL, params=multiple_exact_value_filter(("payer_name", payerName), ("network_status", "INN"))
        ) as resp:
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


async def get_coverage_by_id(session: ClientSession, id: str) -> CPT_code:
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


if __name__ == "__main__":
    import asyncio
    from pprint import pprint

    async def main():

        async with ClientSession(headers=HEADERS) as session:
            both =  await get_coverages_by_payer_name(session, "BCBSTX")
            inn_only = await get_coverages_by_payer_name(session, "BCBSTX", both_inn_and_oon=False)
            pprint(both)
            pprint(inn_only)
            assert len(inn_only) < len(both)
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )  # windows issue
    asyncio.run(main())
