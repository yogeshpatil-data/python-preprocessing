from config.loader import load_config
from logging.logger import setup_logger
from core.exceptions import IngestionError


def main():
    # Load configuration
    config = load_config()

    # Setup logger
    logger = setup_logger(
        name=config["app"]["name"],
        level=config["logging"]["level"]
    )

    logger.info("Application started")
    logger.info(f"Environment: {config['app']['environment']}")

    # Future steps:
    # - API ingestion
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
