from api.client import LastFMApi
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("KEY")


async def main() -> None:
    if KEY:
        async with LastFMApi(api_key=KEY) as client:
            result = await client.artist_get_info(artist="Cher")
            print(result.stats.listeners)


asyncio.run(main())
