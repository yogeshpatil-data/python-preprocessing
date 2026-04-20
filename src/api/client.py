import requests
import json
import time
import logging
import os
from pathlib import Path


logger = logging.getLogger(__name__)
# log_dir = os.path.abspath("practice_log")
# os.mkdir(log_dir)

log_dir = Path("practice_log")
log_dir.mkdir(exist_ok = True)

filehandler = logging.FileHandler(f"{log_dir}/log.txt")
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

logger.addHandler(filehandler)
filehandler.setFormatter(formatter)

logger.setLevel(logging.INFO)

class ExternalAPIError(Exception):
    pass


def fetch_paginated(page_size:int):
    max_retries = 5
    max_backoff = 8
    page  = 1
    base_url = "https://jsonplaceholder.typicode.com/posts"
    timeout = (3,5)  #connection timeout and read timeout


    while True:
        attempt = 0
        backoff = 2

        while attempt <= max_retries:
            param = {
            "_page" : page,
            "_limit" : page_size       
            }

            retryable = True
            logger.info(f"Attempt = {attempt}")

            try:
                response  = requests.get(base_url, params= param,timeout=timeout)
                if response.status_code == 429:
                    raise requests.exceptions.HTTPError("Rate Limited : 429", response=response)
                
                response.raise_for_status()
                data  = response.json()

                if not data:
                    logger.info("Fetching completed")
                    return          #end the API calling

                logger.info(f"Fetching page: {page}")
                yield page, data

                page += 1
                break  # don't process the retry mechanism
            
            except requests.exceptions.RequestException as e:


                #e.reponse because e is the exception object of basae class RequestExc
                #HTTPError is the child class of RequestException class
                #only HTTPError class has the attribute reponse that's why e.reponse
                #reponse is the HTTP response object returned by the  server
                if isinstance(e, requests.exceptions.HTTPError):

                    status  = getattr(e,"status_code", None)

                    if status and 400 <=  status < 500 and status != 429:
                        retryable = False

                if not retryable:
                    logger.error("Bad request", exc_info = True)
                    raise ExternalAPIError from e
                
                if attempt > max_retries:
                    logger.error(f"Max attempt reached: {attempt}", exc_info=True)
                    raise ExternalAPIError("Max Number of retries attempted") from e
                
                logger.warning(f"Retryable API failure backing of after {max_backoff}")

                attempt += 1
                time.sleep(backoff)

                backoff = min(backoff*2, max_backoff)



output_dir = Path("output_files")
output_dir.mkdir(exist_ok = True)

for page, data in fetch_paginated(10):
    file_path = f"{output_dir}/page_{page}.json"

    logger.info(f"Saving File page_{page}.json")

    with open(file_path, "w") as f:
        json.dump(data, f, indent =2)
    print(f"Saved page {page} -> {file_path}")


            



