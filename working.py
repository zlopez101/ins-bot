import aiohttp
import asyncio
from enum impr

class Generate:
    async def __aenter__(self):
        print("entering")
        if not hasattr(self, "session"):
            print("creating")
            self.session = aiohttp.ClientSession()
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        print("exiting")
        await self.session.close()


async def get(sesh: aiohttp.ClientSession):
    async with sesh.get("https://httpbin.org") as resp:
        print(resp.status)


if __name__ == "__main__":

    # async def main():

    #     gen = Generate()
    #     async with gen as session:
    #         await get(session)

    # asyncio.set_event_loop_policy(
    #     asyncio.WindowsSelectorEventLoopPolicy()
    # )  # windows issue
    # asyncio.run(main())
    gen = Generate()
    print(gen.__name__)
