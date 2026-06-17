"""
Entry point for the Florida council agenda scraper.
Run directly: python main.py
Or via cron:  0 6 */5 * * cd /opt/scraper && python main.py >> /var/log/scraper.log 2>&1
"""
import logging
import sys

import db
from scrapers import legistar, civicplus, playwright_scraper, novusagenda, hyland, boarddocs, iqm2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

PLATFORM_MAP = {
    "legistar":    legistar.scrape_municipality,
    "civicplus":   civicplus.scrape_municipality,
    "novusagenda": novusagenda.scrape_municipality,
    "hyland":      hyland.scrape_municipality,
    "boarddocs":   boarddocs.scrape_municipality,
    "iqm2":        iqm2.scrape_municipality,
    "granicus":    None,
    "custom":      playwright_scraper.scrape_municipality,
}


def run() -> None:
    logger.info("=== Flock-Off scraper starting ===")
    municipalities = db.get_active_municipalities()
    logger.info("Loaded %d active municipalities", len(municipalities))

    counts = {"ok": 0, "skip": 0, "error": 0}

    for muni in municipalities:
        platform = muni["platform"]
        scrape_fn = PLATFORM_MAP.get(platform)

        if scrape_fn is None:
            logger.debug("No scraper for platform %r (%s) — skipping", platform, muni["name"])
            counts["skip"] += 1
            continue

        try:
            scrape_fn(muni)
            counts["ok"] += 1
        except Exception as e:
            logger.error("Unhandled error scraping %s: %s", muni["name"], e, exc_info=True)
            counts["error"] += 1

    logger.info(
        "=== Done: %d scraped, %d skipped, %d errors ===",
        counts["ok"], counts["skip"], counts["error"],
    )


if __name__ == "__main__":
    run()
