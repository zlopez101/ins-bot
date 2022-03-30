"""Make Asynchronous API calls to the Airtable API
"""
from typing import List
from aiohttp import ClientSession, ClientResponse, ClientResponseError
from .models import Insurance, CPT_code
from .utils import exact_value_filter, select_fields, filter_unique
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
    async def __aenter__(self) -> ClientSession:
        if not hasattr(self, "session"):
            self.session = ClientSession()
        return self.session

    async def __aexit__(self, _not, sure, why):
        await self.session.close()
        del self.session


async def _raise_for_status(response: ClientResponse, response_object):
    try:
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

    except ClientResponseError as e:
        # tbd
        raise e
    except AttributeError as e:
        # tbd
        pass


async def get_payers(session: ClientSession) -> list:
    params = (
        select_fields("payer_name") + "&" + filter_unique("payer_name", asdict=False)
    )
    # print(params)
    async with session.get(INS_URL + "?" + params, headers=HEADERS) as resp:
        # return await _raise_for_status(resp, Payer)
        res = await resp.json()
        records = res["records"]
        return list(set(record["fields"]["payer_name"] for record in records))


async def get_coverages_by_payer_name(
    session: ClientSession, payerName: str
) -> List[Insurance]:
    async with session.get(
        INS_URL, headers=HEADERS, params=exact_value_filter("payer_name", payerName)
    ) as resp:
        return await _raise_for_status(resp, Insurance)


async def get_coverage_by_id(session: ClientSession, id: str) -> Insurance:
    async with session.get(INS_URL + "/" + id, headers=HEADERS) as resp:
        return await _raise_for_status(resp, Insurance)


async def get_coverage_by_name(session: ClientSession, name: str) -> Insurance:
    # use insurance_name field id -> changes to insurance_name field likely
    async with session.get(
        INS_URL, headers=HEADERS, params=exact_value_filter("insurance_name", name)
    ) as resp:
        return await _raise_for_status(resp, Insurance)


async def get_coverage_by_id(session: ClientSession, id: str) -> CPT_code:
    async with session.get(CPT_URL + "/" + id, headers=HEADERS) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_code_by_code(session: ClientSession, code: str) -> CPT_code:
    async with session.get(
        CPT_URL, headers=HEADERS, params=exact_value_filter("code", code)
    ) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_code_by_exact_name(session: ClientSession, name: str) -> CPT_code:
    async with session.get(
        CPT_URL, headers=HEADERS, params=exact_value_filter("name", name)
    ) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_code_by_name_includes(session: ClientSession, name: str) -> CPT_code:
    async with session.get(
        CPT_URL, headers=HEADERS, params=exact_value_filter("name", name)
    ) as resp:
        return await _raise_for_status(resp, CPT_code)


async def get_cpt_codes_by_type(session: ClientSession, type=str) -> List[CPT_code]:
    """TBD"""
    pass


async def get_financial_classes_by_name(session: ClientSession, name: str) -> dict:
    """TBD"""
    pass
    # async with session.get(FC_URL, headers=HEADERS, params=exact_value_filter('name', name)) as resp:
    # r


if __name__ == "__main__":
    import asyncio
    import pprint

    async def main():

        async with ClientSession(headers=HEADERS) as session:
            async with session.get(
                CPT_URL, params=exact_value_filter("code", "90asdf75f0")
            ) as resp:
                records = await resp.json()
                records = records["records"]
                print(records)
                print(type(records))

    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )  # windows issue
    asyncio.run(main())
