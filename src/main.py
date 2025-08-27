import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
Entry point for the async web scraper.
Handles CLI, logging, and profiling.
"""

import argparse
import asyncio
import logging
import time
import cProfile
import pstats

from src.scraper import scrape


# ---------------- Logging Setup ----------------
logging.basicConfig(
    filename="logs/scraper.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def main() -> None:
    """
    Main entry point for the scraper.
    Handles CLI args, profiling, and execution.
    """
    parser = argparse.ArgumentParser(description="Async Web Scraper with Profiling")
    parser.add_argument("url", help="Base URL to scrape")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to scrape")
    parser.add_argument("--output", default="data/output.csv", help="Output CSV file")
    parser.add_argument("--profile", action="store_true", help="Enable cProfile profiling")
    args = parser.parse_args()

    if args.profile:
        profiler = cProfile.Profile()
        profiler.enable()

    start_time = time.time()
    asyncio.run(scrape(args.url, args.pages, args.output))
    end_time = time.time()

    logging.info(f"Execution time: {end_time - start_time:.2f} seconds")

    if args.profile:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("cumtime")
        stats.dump_stats("scraper_profile.prof")
        logging.info("cProfile data saved to scraper_profile.prof")


if __name__ == "__main__":
    main()
