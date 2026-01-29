import requests #standard http client
import logging
from src.core.exceptions import ExternalAPIError


#Every module should have its own logger
#Name will appear as src.api.client in logs
logger  = logging.getLogger(__name__)

BASE_URL = "https://jsonplaceholder.typicode.com"
MAX_RETRIES = 3
INITIAL_BACKOFF = 1  # seconds
MAX_BACKOFF = 8      # seconds


def fetch_posts():
    url = f"{BASE_URL}/posts"

    timeout = (3,5)
    logger.info("Calling Post API")

    try:
        response = requests.get(url, timeout =  timeout)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        #boundary translation happen here
        logger.error("External API Failed", exc_info= True)
        raise ExternalAPIError("Failed to connect to external API") from e
    

#Connection timeout -> 3 seconds
#Read timeout -> 5 seconds
