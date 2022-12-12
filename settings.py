import json


def get_setting(setting: str) -> str:
    """
    Get the setting from the settings.json file.
    Args:
        setting: The settings string looks like: "DEVICE/LOCATION_ID"
                 with the equivalent jason key being [DEVICE"]["LOCATION_ID"]

    Returns: The value of the json key
    Examples: get_setting("DEVICE/LOCATION_ID")

    See Also: settings.json
    References: settings_example.json

    """
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    keys = setting.split('/')
    value = settings
    for key in keys:
        value = value[key]
    return value
