import logging

from scrape.scraper import scrape_listings

logger = logging.getLogger(__name__)


def main():
    logger.info("Starting scrape...")
    scrape_listings()
    logger.info("Done.")


if __name__ == "__main__":
    main()
