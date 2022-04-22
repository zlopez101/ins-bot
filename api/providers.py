"""Implements all provider calls to the AirTable API"""
from typing import List
from aiohttp import ClientSession
from models.api import Provider
from .methods import _raise_for_status
from .utils import exact_value_filter, URL, HEADERS


async def get_locations(session: ClientSession) -> List[str]:
    """Get the CBC locations

    Args:
        session (ClientSession): session to use
        
    Returns:
        List[str]: List of locations
    """
    async with session.get(URL.PROVIDER_URL.value) as resp:
        results = await resp.json()
        records = results["records"]

        return sorted(set([record["fields"]["Location"] for record in records]))


async def get_providers_at_location(
    session: ClientSession, location: str
) -> List[Provider]:
    async with session.get(
        URL.PROVIDER_URL.value, params=exact_value_filter("Location", location)
    ) as resp:
        return await _raise_for_status(resp, Provider)


if __name__ == "__main__":
    import asyncio

    async def main():
        async with ClientSession(headers=HEADERS) as session:
            print(await get_locations(session))

    asyncio.run(main())
