import asyncio
from typing import Dict, List
from aiohttp import ClientSession, ClientResponse
from attr import field
import requests
from dotenv import load_dotenv
import os
from urllib.parse import quote
from models import Insurance, CPT_code

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
        self.session = ClientSession(headers=self.HEADERS)

    def __aenter__(self):
        return self

    def __aexit__(self):
        return self.close()

    def close(self):
        return self.session.close()

    async def _request(self, endpoint: str, params: dict) -> ClientResponse:
        async with self.session.get(self.BASE_URL + endpoint, params=params) as resp:
            await resp.json()

    async def _post(self, endpoint: str, data: dict) -> ClientResponse:
        async with self.session.get(self.BASE_URL + endpoint, json=data):
            pass

    def _raise_for_status(response: ClientResponse) -> dict:
        pass

    def get_coverages(self):
        params = dict(maxRecords=5)
        return self._request(self.INS_URL, params)

    def __repr__(self):
        return "Async Airtable Client"


class Sync_Checker:
    def __init__(self):
        self.BASE_URL = f"https://api.airtable.com/v0/{os.environ['airtable_base_id']}"
        self.INS_URL = f"/{os.environ['insurance_table_id']}"
        self.CPT_URL = f"/{os.environ['cpt_codes_table_id']}"
        self.HEADERS = {
            "Authorization": f"Bearer {os.environ['API_key']}",
            "Content-Type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def get_coverages(self, maxRecords: int = 5) -> List[Insurance]:
        r = self.session.get(
            self.BASE_URL + self.INS_URL, params=dict(maxRecords=maxRecords)
        )
        return r.json()

    def get_coverages_by_payer_name(self, payerName: str) -> List[Insurance]:
        formula = f'({{payer_name}} = "{payerName}")'
        r = self.session.get(
            self.BASE_URL + self.INS_URL, params=dict(filterByFormula=formula)
        )
        return r.json()

    def get_coverage_by_name(self, coverage_name: str) -> List[Insurance]:
        pass

    def get_cpt_code(self, code: str) -> CPT_code:
        pass

    def create_cpt_code(self, code: CPT_code) -> dict:
        _json = {"fields": code(), "typecast": True}
        r = self.session.post(self.BASE_URL + self.CPT_URL, json=_json)
        return r


if __name__ == "__main__":
    import json
    import time

    synced = Sync_Checker()

    def read() -> list:
        with open("vaccines.json", "r") as fp:
            return json.load(fp)["codes"]

    codes = [CPT_code(**code) for code in read()]

    for code in codes:
        print(code.name)
        resp = synced.create_cpt_code(code)
        print(resp.status_code)
        print(resp.text)
        time.sleep(0.3)

