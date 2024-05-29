from urllib.parse import urlparse

from fastapi import HTTPException, Query, Request, status

from app.config import TIME_PERIODS


def valid_endpoint(request: Request, endpoint: str):
    parsed_url = urlparse(endpoint)

    if not all([parsed_url.scheme, parsed_url.netloc]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Endpoint Provided",
        )

    request.query_params._dict.pop("endpoint", None)

    return endpoint


def valid_limit(request: Request, limit: int = Query(..., gt=0)):
    request.query_params._dict.pop("limit", None)

    return limit


def valid_period(request: Request, period: str):
    try:
        period = TIME_PERIODS[period]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Period Provided",
        )

    request.query_params._dict.pop("period", None)

    return period
