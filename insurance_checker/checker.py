import asyncio
from typing import Dict, List
from aiohttp import ClientSession, ClientResponse
from requests import Response, Session
from dotenv import load_dotenv
import os
from urllib.parse import quote
from models import Insurance, CPT_code, InsuranceFromAPI

load_dotenv()

HEADERS = {
    "Authorization": f"Bearer {os.environ['API_key']}",
    "Content-Type": "application/json",
}
INS_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['insurance_table_id']}"
CPT_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}/{os.environ['cpt_codes_table_id']}"


class Aysnc_Checker:
    def __init__(self):
        self.BASE_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}"
        self.INS_URL = f"/{os.environ['insurance_table_id']}"
        self.CPT_URL = f"/{os.environ['cpt_codes_table_id']}"
        self.HEADERS = {
            "Authorization": f"Bearer {os.environ['API_key']}",
            "Content-Type": "application/json",
        }
        # self.session = ClientSession(headers=self.HEADERS)

    async def __aenter__(self, endpoint: str, **kwargs):
        print("here")
        if not hasattr(self, "session"):
            self.session = ClientSession(headers=self.HEADERS)
        return self.session.get(endpoint, **kwargs)

    async def __aexit__(self):
        return self.session.close()

    def close(self):
        return self.session.close()

    async def _request(self, endpoint: str, params: dict) -> ClientResponse:
        async with self(self.BASE_URL + endpoint, params=params) as resp:
            r = await resp.json()
            print(r)

    async def _post(self, endpoint: str, data: dict) -> ClientResponse:
        async with self.session.get(
            self.BASE_URL + endpoint, json=data, timeout=10
        ) as resp:
            pass

    def _raise_for_status(response: ClientResponse) -> dict:
        pass

    def get_coverages(self):
        params = dict(maxRecords=5)
        return self._request(self.INS_URL, params)

    def __repr__(self):
        return "Async Airtable Client"


class AsyncSession:
    def __init__(self, url):
        self.BASE_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}"
        self.INS_URL = f"/{os.environ['insurance_table_id']}"
        self.CPT_URL = f"/{os.environ['cpt_codes_table_id']}"
        self.HEADERS = {
            "Authorization": f"Bearer {os.environ['API_key']}",
            "Content-Type": "application/json",
        }

    async def __aenter__(self):
        if not hasattr(self, "session"):
            self.session = ClientSession(headers=self.HEADERS)
        response = await self.session.get(self._url)
        return response

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.session.close()

    async def _request(self, endpoint, **kwargs):
        pass


class Sync_Checker:
    def __init__(self):
        self.BASE_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}"
        self.INS_URL = f"/{os.environ['insurance_table_id']}"
        self.CPT_URL = f"/{os.environ['cpt_codes_table_id']}"
        self.HEADERS = {
            "Authorization": f"Bearer {os.environ['API_key']}",
            "Content-Type": "application/json",
        }
        self.session = Session()
        self.session.headers.update(self.HEADERS)

    def _raise_for_status(response: Response) -> dict:
        pass

    def get_coverages(self, maxRecords: int = 5) -> List[Insurance]:
        r = self.session.get(
            self.BASE_URL + self.INS_URL, params=dict(maxRecords=maxRecords)
        )
        return r.json()

    def get_coverages_by_payer_name(self, payerName: str) -> List[Insurance]:
        formula = f'({{payer_name}} = "{payerName}")'
        params = dict(filterByFormula=formula)
        r = self.session.get(self.BASE_URL + self.INS_URL, params=params)
        return r

    def get_coverage_by_id(self, id: str) -> Insurance:
        return self.session.get(self.BASE_URL + self.INS_URL + f"/{id}")

    def get_coverage_by_name(self, coverage_name: str) -> List[Insurance]:
        formula = f'({{insurance_name}} =  "{coverage_name}")'
        params = dict(filterByFormula=formula)
        r = self.session.get(self.BASE_URL + self.INS_URL, params=params)
        return r

    def get_cpt_code(self, code: str) -> CPT_code:
        formula = f'({{code}} =  "{code}")'
        params = dict(filterByFormula=formula)
        r = self.session.get(self.BASE_URL + self.CPT_URL, params=params)
        return r

    def create_cpt_code(self, code: CPT_code) -> dict:
        _json = {"fields": code(), "typecast": True}
        r = self.session.post(self.BASE_URL + self.CPT_URL, json=_json)
        return r.json()


async def _get(session: ClientSession, endpoint: str, **kwargs) -> ClientResponse:
    pass


async def _post(session: ClientSession, endpoint: str, **kwargs) -> ClientResponse:
    pass


if __name__ == "__main__":
    pass
