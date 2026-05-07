import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sys
import os

# Mock DB for testing
class MockDB:
    def add_knowledge_fact(self, *args, **kwargs):
        print(f"Adding fact: {args[0][:30]}...")
    def get_knowledge_count(self):
        return 3075

async def test_sources():
    urls = [
        "https://www.nuprc.gov.ng",
        "https://neiti.gov.ng/index.php/reports/oil-and-gas-reports"
    ]
    async with aiohttp.ClientSession() as session:
        for url in urls:
            print(f"Testing {url}...")
            try:
                async with session.get(url, timeout=5) as resp:
                    print(f"Status: {resp.status}")
                    text = await resp.text()
                    print(f"Content length: {len(text)}")
            except Exception as e:
                print(f"Failed {url}: {e}")

if __name__ == "__main__":
    asyncio.run(test_sources())
