"""Make Asynchronous API calls to the Airtable API
"""
from typing import List
from aiohttp import ClientSession, ClientResponse
from models import Insurance, CPT_code, InsuranceFromAPI
from utils import field_filter
from dotenv import load_dotenv
import os

load_dotenv()

HEADERS = {
    "Authorization": f"Bearer {os.environ['API_key']}",
    "Content-Type": "application/json",
}
INS_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['insurance_table_id']}"
CPT_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['cpt_codes_table_id']}"


async def get_coverages_by_payer_name(
    session: ClientSession, payerName: str
) -> List[Insurance]:
    async with session.get(
        INS_URL, headers=HEADERS, params=field_filter("payer_name", payerName)
    ) as resp:
        coverages = await resp.json()
        return [Insurance.from_api(record) for record in coverages["records"]]


async def get_coverage_by_id(session: ClientSession, id: str) -> Insurance:
    pass


async def get_coverage_by_name(session: ClientSession, name: str) -> Insurance:
    pass


async def get_cpt_code_by_code(session: ClientSession, code: str) -> CPT_code:
    params = field_filter("code", code)
    async with session.get(CPT_URL, headers=HEADERS, params=params) as resp:
        cpt_code = await resp.json()
        return cpt_code


async def get_financial_classes_by_id(session: ClientSession, id: str) -> dict:
    pass


if __name__ == "__main__":
    import asyncio

    async def main():

        async with ClientSession() as session:
            print(await get_cpt_code_by_code(session, "90750"))

    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )  # windows issue
    asyncio.run(main())

