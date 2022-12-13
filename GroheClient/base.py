import logging
from datetime import datetime, timedelta

from GroheClient.tokens import get_refresh_tokens, get_tokens_from_credentials
from settings import get_setting as _


def get_initial_tokens() -> dict:
    """
    Get the initial access and refresh tokens.
    Returns: A dict with the tokens.

    """
    return get_tokens_from_credentials(_("CREDENTIALS/EMAIL"), _("CREDENTIALS/PASSWORD"))


# get the initial tokens
try:
    initial_tokens = get_initial_tokens()
except Exception as e:
    logging.error("Could not get initial tokens: {}".format(e))
    exit(1)

# set the tokens
# noinspection PyUnboundLocalVariable
access_token = initial_tokens['access_token']
access_token_expiring_date = datetime.now() + timedelta(seconds=initial_tokens['access_token_expires_in'] - 60)
refresh_token = initial_tokens['refresh_token']


def refresh_tokens():
    logging.info("Refreshing tokens")
    global access_token, refresh_token, access_token_expiring_date
    tokens = get_refresh_tokens(refresh_token)
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    access_token_expiring_date = datetime.now() + timedelta(seconds=tokens['access_token_expires_in'] - 60)


def get_access_token() -> str:
    """
    Get the access token. Refresh the tokens if they are expired.
    Returns: The access token.

    """
    global access_token, access_token_expiring_date
    # refresh the tokens if they are expired
    if datetime.now() > access_token_expiring_date:
        refresh_tokens()

    return access_token
