import json
from datetime import datetime, timedelta

import requests
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from settings import get_setting as _

AUTH_BASE_URL = "https://idp2-apigw.cloud.grohe.com/v3/iot/oidc/login"
REFRESH_TOKEN_BASE_URL = "https://idp2-apigw.cloud.grohe.com/v3/iot/oidc/refresh"

CREDENTIALS_PASSWORD = _("CREDENTIALS/PASSWORD")
CREDENTIALS_EMAIL = _("CREDENTIALS/EMAIL")


def process_browser_log_entry(entry: dict) -> dict:
    """
    Process a browser log entry and return a dict with the method and params.
    Args:
        entry: A browser log entry.

    Returns: A dict with the method and params.

    """
    response = json.loads(entry['message'])['message']
    return response


def refresh_tokens() -> dict:
    """
    Refresh the access and refresh tokens.
    Returns: A dict with the new tokens.

    """
    data = {
        'refresh_token': refresh_token,
    }
    response = requests.post(REFRESH_TOKEN_BASE_URL, json=data)
    response.raise_for_status()

    tokens = get_tokens_from_json(response.json())
    return tokens


def get_initial_tokens() -> dict:
    """
    Get the initial access and refresh tokens.
    Returns: A dict with the tokens.

    """
    # set chrome driver options
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')
    options.add_argument('disable-gpu')
    options.add_argument('no-sandbox')

    # enable browser network logging
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities=caps, options=options)
    driver.get(AUTH_BASE_URL)

    # wait for the login form to appear
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CLASS_NAME, 'form-group'))
    )

    # get the input fields
    email_input = driver.find_element(By.ID, 'username')
    password_input = driver.find_element(By.ID, 'password')
    submit_button = driver.find_element(By.CLASS_NAME, 'btn-primary')

    # fill in the login data
    email_input.send_keys(CREDENTIALS_EMAIL)
    password_input.send_keys(CREDENTIALS_PASSWORD)

    # submit the form
    submit_button.click()

    # get all entries from browser network tab
    browser_log = driver.get_log('performance')
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.response' in event['method']]

    # get the response from the refresh token request and extract the token url
    ondus_key_url = events[-1]['params']['headers']['location']
    tokens_url = ondus_key_url.replace('ondus://', 'https://')

    # get the tokens from the token url
    driver.get(tokens_url)

    # get the json from the page
    json_text = driver.find_element(By.TAG_NAME, 'pre').text

    # close the browser
    driver.quit()

    # get the tokens from the json
    tokens = get_tokens_from_json(json.loads(json_text))

    return tokens


def get_tokens_from_json(json_data: dict) -> dict:
    """
    Get the tokens from the json data.
    Args:
        json_data: The json data.

    Returns: A dict with the tokens.

    """
    tokens = {
        'access_token'           : json_data['access_token'],
        'access_token_expires_in': json_data['expires_in'],
        'refresh_token'          : json_data['refresh_token'],
        'refresh_token_expires_in': json_data['refresh_expires_in'],
    }
    return tokens


# get the initial tokens
initial_tokens = get_initial_tokens()

# set the tokens
access_token = initial_tokens['access_token']
access_token_expiring_date = datetime.now() + timedelta(seconds=initial_tokens['access_token_expires_in'] - 60)
refresh_token = initial_tokens['refresh_token']


def get_access_token() -> str:
    """
    Get the access token. Refresh the tokens if they are expired.
    Returns: The access token.

    """
    global access_token
    global refresh_token
    global access_token_expiring_date

    # refresh the tokens if they are expired
    if datetime.now() > access_token_expiring_date:
        tokens = refresh_tokens()
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        access_token_expiring_date = datetime.now() + timedelta(seconds=tokens['access_token_expires_in'] - 60)

    return access_token
