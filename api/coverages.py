"""Implements all coverage calls to the Airtable API"""

from typing import List, Tuple
from aiohttp import ClientSession
from models.api import Insurance
from .utils import (
    exact_value_filter,
    multiple_exact_value_filter,
    URL,
)
from .methods import _list_records, _retrieve_record, _patch_record


async def get_payers(session: ClientSession) -> List[str]:
    """Get the payer names. This method won"""
    coverages, _ = await _list_records(session, URL.INS_URL.value, Insurance)
    return sorted(set([coverage.payer_name for coverage in coverages]))


async def get_coverages_by_payer_name(
    session: ClientSession,
    payerName: str,
    inn_only: bool = True,
    pageSize: int = 5,
    offset: str = None,
) -> Tuple[List[Insurance], str]:
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
        params = multiple_exact_value_filter(
            ("payer_name", payerName), ("network_status", "INN")
        )
    else:
        params = exact_value_filter("payer_name", payerName)

    return await _list_records(
        session,
        URL.INS_URL.value,
        Insurance,
        params=params,
        pageSize=pageSize,
        offset=offset,
    )


async def get_coverage_by_id(session: ClientSession, id: str) -> Insurance:
    return _retrieve_record(session, URL.INS_URL.value, id, Insurance)


async def get_coverage_by_name(session: ClientSession, name: str) -> Insurance:
    """Get the coverage by the name selected by user

    Args
        name (str): name of the insurance the user selected

    Returns:
        Insurance: Insurance object to be returned. 
    """
    records, offset = await _list_records(
        session,
        URL.INS_URL.value,
        Insurance,
        params=exact_value_filter("insurance_name", name),
    )
    # the patching of the record does not affect the user. the `GET` object
    # is the one returned
    await _patch_record(
        session,
        URL.INS_URL.value,
        records[0].id,
        {"time_requested": records[0].time_requested + 1,},
    )
    return records, offset


async def get_financial_classes_by_name(session: ClientSession, name: str) -> dict:
    """TBD"""
    pass


if __name__ == "__main__":
    from .utils import HEADERS
    import asyncio

    async def main():
        async with ClientSession(headers=HEADERS) as session:
            record = await get_coverage_by_name(session, "BCBSTX UT Select PPO")
            print(record)

    asyncio.run(main())
