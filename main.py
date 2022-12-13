import logging

import fastapi
import uvicorn
from fastapi import HTTPException, Security
from fastapi.openapi.models import APIKey
from fastapi.params import Depends
from fastapi.responses import Response
from fastapi.security.api_key import APIKeyCookie, APIKeyHeader, APIKeyQuery
from starlette.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_412_PRECONDITION_FAILED, HTTP_500_INTERNAL_SERVER_ERROR
)

from GroheClient.tap_controller import check_tap_params, execute_tap_command
from settings import get_setting as _

BIND_ADDRESS = _("SERVER/BIND_ADDRESS")
BIND_PORT = _("SERVER/BIND_PORT")

API_KEY = _("API/API_KEY")
API_KEY_NAME = "API_KEY"

API_KEY_QUERY = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
API_KEY_COOKIE = APIKeyCookie(name=API_KEY_NAME, auto_error=False)

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


async def get_api_key(api_key_query: str = Security(API_KEY_QUERY),
                      api_key_header: str = Security(API_KEY_HEADER)) -> str:
    """
    Returns the API key from the query or header.
    Args:
        api_key_query: The API key from the query.
        api_key_header: The API key from the header.

    Returns: The API key.
    Raises: HTTPException if the API key is invalid.

    """
    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    else:
        logging.error(f"Invalid API key: {api_key_query} {api_key_header}")
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")


app = fastapi.FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/tap/{tap_type}/{amount}")
@app.post("/tap/{tap_type}/{amount}")
def tap(tap_type: int, amount: int, api_key: APIKey = Depends(get_api_key)) -> Response:
    """
    Executes the command for the given tap type and amount.
    Args:
        tap_type: The type of tap. 1 for still, 2 for medium, 3 for sparkling.
        amount: The amount of water to be dispensed in ml.
        api_key: The API key to use.

    Returns: The response containing the result of the command.
    Raises: HTTPException if the command was not executed successfully or a precondition failed.

    """
    try:
        success = execute_tap_command(tap_type, amount)
        if not success:
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not execute command")
        return fastapi.Response(status_code=HTTP_201_CREATED)
    except ValueError as e:
        raise HTTPException(status_code=HTTP_412_PRECONDITION_FAILED, detail=str(e))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not execute command")


@app.head("/tap/{tap_type}/{amount}")
def tap_head(tap_type: int, amount: int) -> Response:
    """
    Returning a 200 OK response for the given tap type and amount.
    Args:
        tap_type: The type of tap. 1 for still, 2 for medium, 3 for sparkling.
        amount: The amount of water to be dispensed in ml.

    Returns: The response containing a 200 status code.
    Raises: HTTPException if the values are invalid.

    See Also: GroheClient.tap_controller.check_tap_params

    """
    try:
        check_tap_params(tap_type, amount)
    except ValueError as e:
        raise HTTPException(status_code=HTTP_412_PRECONDITION_FAILED, detail=str(e))

    return fastapi.Response(status_code=HTTP_200_OK)


if __name__ == "__main__":
    uvicorn.run(app, host=BIND_ADDRESS, port=int(BIND_PORT))
