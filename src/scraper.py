"""
Async scraping logic using aiohttp with retry, resource logging, and live currency conversion.
"""

import asyncio
import aiohttp
import logging
import os
import random
import psutil
from typing import List, Dict
from aiohttp import ClientSession, ClientTimeout

from src.parser import parse_page
from src.exporter import save_to_csv  # or src.storage if you renamed
import config
from src.utils.currency import LiveFx  # new helper for GBP→INR

async def fetch(session: ClientSession, url: str, retries: int = config.MAX_RETRIES, delay: int = config.RETRY_DELAY) -> str:
    """
    Fetch a single page with retry logic.
    """
    headers = {"User-Agent": random.choice(config.USER_AGENTS)}

    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                logging.error(f"Failed {url} with status {response.status}")
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")

        await asyncio.sleep(delay * (attempt + 1))

    return None


def log_resource_usage() -> None:
    """
    Log memory and CPU usage of the process.
    """
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    cpu_percent = psutil.cpu_percent(interval=0.5)
    logging.info(
        f"Memory RSS: {mem_info.rss / 1024**2:.2f} MB | "
        f"VMS: {mem_info.vms / 1024**2:.2f} MB | "
        f"CPU: {cpu_percent}%"
    )


async def scrape(base_url: str, pages: int, output: str) -> None:
    """
    Scrape multiple pages asynchronously, convert GBP→INR, and save results.
    """
    all_data: List[Dict[str, str]] = []
    timeout = ClientTimeout(total=config.REQUEST_TIMEOUT)

    # 🔹 Get live GBP→INR rate once
    fx = LiveFx(base="GBP", target="INR", ttl_seconds=3600)
    try:
        gbp_to_inr = fx.get_rate()
        logging.info(f"Live FX rate: 1 GBP = {gbp_to_inr:.2f} INR")
    except Exception as e:
        logging.error(f"Could not fetch live FX rate: {e}")
        gbp_to_inr = None

    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [fetch(session, f"{base_url}?page={page}") for page in range(1, pages + 1)]

        for future in asyncio.as_completed(tasks):
            html = await future
            page_data = parse_page(html)

            # 🔹 Add INR conversion
            if gbp_to_inr:
                for row in page_data:
                    gbp_val = row.get("Price_GBP")
                    if isinstance(gbp_val, (int, float)):
                        row["Price_INR"] = round(gbp_val * gbp_to_inr, 2)
                    else:
                        row["Price_INR"] = None

            all_data.extend(page_data)
            log_resource_usage()

    save_to_csv(all_data, output)
    logging.info(f"✅ Scraping finished. Saved {len(all_data)} records to {output}")
