import logging
import time

import requests

from GroheClient.base import get_access_token, refresh_tokens
from settings import get_setting as _

DEVICE_LOCATION_ID = _("DEVICE/LOCATION_ID")
DEVICE_APPLIANCE_ID = _("DEVICE/APPLIANCE_ID")
DEVICE_ROOM_ID = _("DEVICE/ROOM_ID")

APPLIANCE_COMMAND_URL = f'https://idp2-apigw.cloud.grohe.com/v3/iot' \
                        f'/locations/{DEVICE_LOCATION_ID}' \
                        f'/rooms/{DEVICE_ROOM_ID}' \
                        f'/appliances/{DEVICE_APPLIANCE_ID}' \
                        f'/command'


def get_auth_header(access_token: str) -> str:
    """
    Returns the authorization header for the given access token.
    Args:
        access_token: The access token to use.

    Returns: The authorization header.

    """
    return f'Bearer {access_token}'


def execute_tap_command(tap_type: int, amount: int, tries=0) -> bool:
    """
    Executes the command for the given tap type and amount.
    Args:
        tap_type: The type of tap. 1 for still, 2 for medium, 3 for sparkling.
        amount: The amount of water to be dispensed in ml.
        tries: The number of tries to execute the command.

    Returns: True if the command was executed successfully, False otherwise.

    """
    check_tap_params(tap_type, amount)

    # set the headers
    headers = {
        "Content-Type" : "application/json",
        "Authorization": get_auth_header(get_access_token()),
    }

    # set the payload body
    data = {
        "type"        : None,
        "appliance_id": DEVICE_APPLIANCE_ID,
        "command"     : get_command(tap_type, amount),
        "commandb64"  : None,
        "timestamp"   : None
    }

    # send the request
    response = requests.post(APPLIANCE_COMMAND_URL, headers=headers, json=data)
    response.raise_for_status()

    tries += 1

    if response.ok:
        return True

    logging.error(f'Failed to execute tap command. Response: {response.text}')

    # check for a server error
    if response.status_code >= 500:
        # wait 5 seconds and try again
        time.sleep(5)
        # small amount of tries to execute the command, otherwise water will be dispensed after the user expects it
        if tries < 2:
            return execute_tap_command(tap_type, amount, tries + 1)

    # if the authorization token is invalid, refresh the tokens and try again
    if response.status_code == 401 and tries < 3:
        logging.info('Refreshing tokens and trying again.')
        refresh_tokens()
        return execute_tap_command(tap_type, amount, tries + 1)

    # try again once after 5 seconds if the request failed
    if tries < 2:
        time.sleep(5)
        return execute_tap_command(tap_type, amount, tries + 1)

    return False


def check_tap_params(tap_type: int, amount: int) -> None:
    """
    Checks the given tap parameters.
    Args:
        tap_type: The type of tap. 1 for still, 2 for medium, 3 for sparkling.
        amount: The amount of water to be dispensed in ml.

    Raises: ValueError if the parameters are invalid.

    """
    # check if the tap type is valid
    if tap_type not in [1, 2, 3]:
        raise ValueError(f'Invalid tap type: {tap_type}. Valid values are 1, 2 and 3.')
    # check if the amount is valid
    if amount % 50 != 0 or amount <= 0 or amount > 2000:
        raise ValueError('The amount must be a multiple of 50, greater than 0 and less or equal to 2000.')


def get_command(tap_type: int, amount: int) -> dict:
    """
    Returns the command to execute for the given tap type and amount.
    Args:
        tap_type: The type of tap. 1 for still, 2 for medium, 3 for sparkling.
        amount: The amount of water to be dispensed in ml.

    Returns: The command to execute.

    """
    return {
        "co2_status_reset"         : False,
        "tap_type"                 : tap_type,
        "cleaning_mode"            : False,
        "filter_status_reset"      : False,
        "get_current_measurement"  : False,
        "tap_amount"               : amount,
        "factory_reset"            : False,
        "revoke_flush_confirmation": False,
        "exec_auto_flush"          : False
    }
