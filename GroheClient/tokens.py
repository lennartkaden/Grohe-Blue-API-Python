import json

import requests
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


REFRESH_TOKEN_BASE_URL = "https://idp2-apigw.cloud.grohe.com/v3/iot/oidc/refresh"
AUTH_BASE_URL = "https://idp2-apigw.cloud.grohe.com/v3/iot/oidc/login"


def get_tokens_from_credentials(grohe_email: str, grohe_password: str) -> dict:
    """
    Get the initial access and refresh tokens from the given grohe credentials.
    Args:
        grohe_email: The grohe email.
        grohe_password: The grohe password.

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
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'form-group')))

    # get the input fields
    email_input = driver.find_element(By.ID, 'username')
    password_input = driver.find_element(By.ID, 'password')
    submit_button = driver.find_element(By.CLASS_NAME, 'btn-primary')

    # fill in the login data
    email_input.send_keys(grohe_email)
    password_input.send_keys(grohe_password)

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


def process_browser_log_entry(entry: dict) -> dict:
    """
    Process a browser log entry and return a dict with the method and params.
    Args:
        entry: A browser log entry.

    Returns: A dict with the method and params.

    """
    response = json.loads(entry['message'])['message']
    return response


def get_tokens_from_json(json_data: dict) -> dict:
    """
    Get the tokens from the json data.
    Args:
        json_data: The json data.

    Returns: A dict with the tokens.

    """
    tokens = {
        'access_token' : json_data['access_token'], 'access_token_expires_in': json_data['expires_in'],
        'refresh_token': json_data['refresh_token'], 'refresh_token_expires_in': json_data['refresh_expires_in'],
    }
    return tokens


def get_refresh_tokens(refresh_token: str) -> dict:
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
