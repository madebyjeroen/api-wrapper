import logging
from asyncio import sleep
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import aiohttp
import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Request, status
from xxhash import xxh64

from app.cache import retrieve_session, update_session
from app.config import FORBIDDEN_HEADERS, settings
from app.dependencies import valid_endpoint, valid_limit, valid_period

app = FastAPI(openapi_url=None)


# SLIDING WINDOW RATE LIMITING
@app.get("/")
async def root(
    request: Request,
    endpoint: str = Depends(valid_endpoint),
    limit: int = Depends(valid_limit),
    period: timedelta = Depends(valid_period),
):
    params = dict(request.query_params)
    headers = dict(request.headers)
    session = headers.pop("session", None)
    retries = 0

    for key in FORBIDDEN_HEADERS:
        headers.pop(key, None)

    if not session:
        base_url = urlparse(endpoint).netloc
        session = xxh64(
            f"{request.client.host}:{base_url}:{limit}:{period}".encode("utf-8")
        ).hexdigest()

    logging.info(f"session:{session}")

    while retries < settings.max_retries:
        previous_requests = np.array(await retrieve_session(session), np.datetime64)
        current_date = datetime.now(timezone.utc)
        start_of_period = np.datetime64(current_date - period)
        requests_in_period = np.sort(
            previous_requests[previous_requests > start_of_period]
        )
        number_of_requests_in_period = len(requests_in_period)

        if number_of_requests_in_period > 0:
            earliest_request = requests_in_period[0].astype(datetime)
            latest_request = requests_in_period[-1].astype(datetime)

            time_left_of_period = (
                period - (latest_request - earliest_request)
            ).total_seconds()
            requests_remaining_for_period = limit - number_of_requests_in_period

            if requests_remaining_for_period <= 0:
                seconds_until_new_request = period.total_seconds() / limit
            else:
                seconds_until_new_request = (
                    time_left_of_period / requests_remaining_for_period
                )

            await update_session(
                session,
                current_date + timedelta(seconds=seconds_until_new_request),
                period,
            )

            logging.info(f"waiting for {seconds_until_new_request} seconds")
            await sleep(seconds_until_new_request)
        else:
            await update_session(session, current_date, period)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                endpoint, params=params, headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logging.warning(
                        f"too many requests{', retrying...' if retries < settings.max_retries else None}"
                    )

                    retries += 1
                else:
                    logging.error(f"invalid request ({response.status})")

                    raise HTTPException(status_code=response.status)

    raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
