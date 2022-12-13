import json
import uuid

import requests
import simplejson as simplejson

from GroheClient.tokens import get_tokens_from_credentials

LOCATIONS_BASE_URL = "https://idp2-apigw.cloud.grohe.com/v3/iot/locations"
ROOMS_BASE_URL = "https://idp2-apigw.cloud.grohe.com/v3/iot/locations/{}/rooms"
APPLIANCES_BASE_URL = "https://idp2-apigw.cloud.grohe.com/v3/iot/locations/{}/rooms/{}/appliances"


class Location:
    def __init__(self, location_id: str, name: str):
        self.location_id = location_id
        self.name = name

    def __repr__(self):
        return f"Location({self.location_id}, {self.name})"

    def __str__(self):
        return self.name


class Room:
    def __init__(self, location: Location, room_id: str, name: str):
        self.location = location
        self.room_id = room_id
        self.name = name

    def __repr__(self):
        return f"Room({self.location} - {self.room_id}, {self.name})"

    def __str__(self):
        return self.name


class Device:
    def __init__(self, room: Room, appliance_id: str, type_id: int, name: str):
        self.room = room
        self.appliance_id = appliance_id
        self.type_id = type_id
        self.name = name

    def __repr__(self):
        return f"Device({self.room} - {self.appliance_id}, {self.name})"

    def __str__(self):
        return self.name


print("""
  █████████  ██████████ ███████████ █████  █████ ███████████
 ███░░░░░███░░███░░░░░█░█░░░███░░░█░░███  ░░███ ░░███░░░░░███
░███    ░░░  ░███  █ ░ ░   ░███  ░  ░███   ░███  ░███    ░███
░░█████████  ░██████       ░███     ░███   ░███  ░██████████
 ░░░░░░░░███ ░███░░█       ░███     ░███   ░███  ░███░░░░░░
 ███    ░███ ░███ ░   █    ░███     ░███   ░███  ░███
░░█████████  ██████████    █████    ░░████████   █████
 ░░░░░░░░░  ░░░░░░░░░░    ░░░░░      ░░░░░░░░   ░░░░░

Use this script to obtain necessary information about your Grohe blue devices.

This scrip will obtain the following information from Grohe for the API to work:
    - The Location IDs of all your Homes created in the Grohe app
    - The Room IDs of all your Rooms created in the Grohe app
    - The Appliance IDs of all your Connected Devices
    - The Type ID of your Connected Device to determine if it is a Grohe Blue device.

You need to provide the following information:
    - Your Grohe Ondus / Watersystems Email Address
    - Your Grohe Ondus / Watersystems Password

This script will also create a settings.json file with the information about you selected Device and geneal settings.
""")

# check if a settings.json file already exists
try:
    with open('settings.json', 'r') as f:
        settings = json.load(f)
    print("settings.json already exists. Please delete it if you want to run this script again.")
    exit(0)
except FileNotFoundError:
    pass


grohe_email = input("Enter your Grohe Ondus / Watersystems Email Address: ")
grohe_password = input("Enter your Grohe Ondus / Watersystems Password: ")

# get the initial tokens
try:
    tokens = get_tokens_from_credentials(grohe_email, grohe_password)
except Exception as e:
    print(e)
    print("Could not get initial tokens. Please check your email and password.")
    exit(1)

print("Tokens obtained successfully. Searching for your Grohe Blue device...")
# noinspection PyUnboundLocalVariable
request_headers = {
    "Authorization": "Bearer " + tokens['access_token'],
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# get the locations
locations = []
print("Found the following locations:")
for location in requests.get(LOCATIONS_BASE_URL, headers=request_headers).json():
    locations.append(
        Location(location['id'], location['name'])
    )
    print(f"    - {location['name']} ({location['id']})")

print("")

# get the rooms
rooms = []
print("Found the following rooms:")
for location in locations:
    for room in requests.get(ROOMS_BASE_URL.format(location.location_id), headers=request_headers).json():
        rooms.append(
            Room(location, room['id'], room['name'])
        )
        print(f"    - {room['name']} ({room['id']})")

print("")

# get the devices
devices = []
print("Found the following devices:")
for room in rooms:
    for index, device in enumerate(requests.get(APPLIANCES_BASE_URL.format(room.location.location_id, room.room_id),
                                   headers=request_headers).json()):
        devices.append(
            Device(room, device['appliance_id'], device['type'], device['name'])
        )
        print(f"    {index}: {device['name']} ({device['appliance_id']})")

print("\nPlease enter the ID of the device you want to use with this script.")
device_id = int(input("Device ID: "))
device = devices[device_id]
print(f"Selected device: {device}")

print("\nYou obtained all the necessary information from Grohe!")
print("Now you need to enter 3 more pieces of information to complete the setup.\n")

bind_address = input("Enter the IP address which the script should bind to (leave empty for 127.0.0.1): ")
if bind_address == "":
    bind_address = "127.0.0.1"

print(f"Binding to {bind_address}")

bind_port = input("Enter the port which the script should bind to (leave empty for 8000): ")
if bind_port == "":
    bind_port = 8000
else:
    bind_port = int(bind_port)

print(f"Binding to port {bind_port}")

print("\nThe last step is to enter a SECURE API key which you will need to use to access the API.")
api_key = input("Enter a secure API key (leave empty for a random key): ")
if api_key == "":
    api_key = uuid.uuid4()

print(f"Using API key: {api_key}")

print("\nSaving settings to settings.json...")
with open("settings.json", "w") as settings_file:
    settings = {
        "DEVICE"     : {
            "LOCATION_ID" : device.room.location.location_id,
            "ROOM_ID"     : device.room.room_id,
            "APPLIANCE_ID": device.appliance_id,
        },
        "CREDENTIALS": {
            "EMAIL"   : grohe_email,
            "PASSWORD": grohe_password
        },
        "API"        : {
            "API_KEY": str(api_key),
        },
        "SERVER"     : {
            "BIND_ADDRESS": bind_address,
            "BIND_PORT"   : bind_port
        }
    }
    settings_file.write(simplejson.dumps(settings, indent=4, sort_keys=True))

print("Done! You can now start the API with 'python3 main.py'")
print("")
print("If you want to change the settings later, you can edit the settings.json file.")
