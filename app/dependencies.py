from typing import Annotated

from fastapi import HTTPException, Request, status
from pydantic import AfterValidator, HttpUrl, PositiveInt

from app.config import TIME_PERIODS


def valid_endpoint(request: Request, endpoint: Annotated[HttpUrl, AfterValidator(str)]):
    request.query_params._dict.pop("endpoint", None)

    return endpoint


def valid_limit(request: Request, limit: PositiveInt):
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
