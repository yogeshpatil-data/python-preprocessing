from src.config.loader import load_config
from src.logging.logger import setup_logging, get_logger
from src.core.exceptions import IngestionError
from src.api.client import fetch_posts, fetch_post_paginated


def main():
    setup_logging()

# this is a named logger for the module, its message ultimately bubbles up to the root logger
    logger = get_logger(__name__)
    logger.info("Application started")
    
    ###################################
    # - API ingestion wihout pagination
    try:
        posts = fetch_posts()
        logger.info(f"fetched {len(posts)} posts")

    except IngestionError:
        logger.error("API call failed", exc_info=True)
        raise

   ###################################
   #API ingestion with pagination
    count = 0

    try:
        for post in fetch_post_paginated(page_size=10):
            count += 1

        logger.info(f"Fetched total {count} posts")

    except IngestionError:
        logger.error("Ingestion pipeline failed", exc_info=True)
        raise




    # - File operations
    # - DB writes

    logger.info("Application finished successfully")


if __name__ == "__main__":
    try:
        main()
    except IngestionError as e:
        print(f"Controlled ingestion failure: {e}")
        raise
    except Exception as e:
        print(f"Unhandled system failure: {e}")
        raise
