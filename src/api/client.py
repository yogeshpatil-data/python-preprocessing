import requests #standard http client
import logging
import time
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

    timeout = (3,5)  # in request if we pass a tuple that means (connection timeout, read timeout)
    logger.info("Calling Post API")
    attempts = 0

    while attempts < MAX_RETRIES:
       attempt += 1
       backoff = INITIAL_BACKOFF
       logger.info("API call attempt {attempt}")

       try:
            response = requests.get(url, timeout =  timeout)
            if response.status_code == 429:
               raise requests.exception.HTTPError(
                  "Rate limited 429", response=response
               )
            
            response.raise_for_status()
            return response.json()

       #we will decide what to do with the error we got
       except requests.exceptions.RequestException as e:
            
            #Decide if retryable, set default true
            retryable = True

            # Here we are checking that the exception object(instance) e is the of type HTTPError
            if isinstance(e, requests.exceptions.HTTPError):

                #e.reponse because e is the exception object of basae class RequestExc
                #HTTPError is the child class of RequestException class
                #only HTTPError class has the attribute reponse that's why e.reponse
                #reponse is the HTTP response object returned by the  server
                status =  getattr(e.repsonse, "status_code", None)

                if status and 400<= status < 500 and status != 429:
                    #A bad client request is not retryable
                    retryable = False

            if not retryable:
                logger.error("Non retryable API failure", exc_info=True)
                raise ExternalAPIError("External API rejected the request") from e
            
            if attempt>= MAX_RETRIES:
                logger.error("API failed after max retired", exc_info=True)
                raise ExternalAPIError ("External API failed after retries") from e
            
            logger.warning(f"Retryable API failure backing of after {MAX_BACKOFF}")

            time.sleep(backoff)
            backoff = min(backoff*2, MAX_BACKOFF)


#page_size is decided by API, we can request a page of certain size but it depends on API


# afunction with yeild keyword is the generator function
def fetch_post_paginated(page_size = 10):
    page  = 1
    timeout = (3,5)

    while True:

        params = {
            "_page" : page,
            "_limit" : page_size
        }

        logger.info(f"fetching page {page}")

        try:
            response =  requests.get(url, params = params, timeout = timeout)
            response.raise_for_status()
            data = response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"External API call failed")
            raise ExternalAPIError(f"API call failed") from e
        
        #this is page level logic
        #if no records returned while requesting next page that means pagination completed

        if not data:
            logger.info(f"No more data returned pagination complete")
            break

        #this is record level logic, iteration over the records returned in one set of 'data'
        for record in data:
            yield record   #yeild makes this whole function a generator
        
        page += 1
