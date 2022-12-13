# HTTP Tap Control API for Grohe Blue Device
Use this API to dispense water from your Grohe Blue device.
The API uses the Grohe IOT API which is used by the Grohe Blue app.
The API is not publicly documented and may change at any time.

## Usages
The API is ment to help you to integrate your Grohe Blue device into your home automation system.
This could be done by using the API directly, by using a Home Assistant integration or Homebridge plugins for example.

## Installation
Clone the Repository
```bash
git clone https://github.com/lennartkaden/Grohe-Blue-API-Python.git
```
and install the requirements:
```bash
pip install -r requirements.txt
```

You may need to use `pip3` instead of `pip`.
Depending on your installation you may also need to install google-chrome-stable and chromedriver.  

Install Google Chrome from [here](https://www.google.com/chrome/).  
To install chromedriver, follow the instructions on the [chromedriver website](https://chromedriver.chromium.org/getting-started).

## Setup
To simplify the setup process, you can use the `install.py` script. It will guide you through the setup process.
```bash
python install.py
```
This will create a `settings.json` file in the root directory of the project.
All information needed to connect to your Grohe Blue device is stored in this file.

If you choose to use you own API key, keep the following in mind:

| :exclamation:  The `API_KEY` under `API` has to be unique and secure! |
|-----------------------------------------------------------------------|
Otherwise, anyone with access to the API can use it to dispense water from your Grohe Blue device.

Because of this, the `install.py` script will generate a random API key for you if you don't provide one.

## Usage
To start the API, run the following command:
```bash
python3 main.py
```
Currently, the API only supports the following endpoint:
```
GET /tap/{tap_type}/{amount}
PUSH /tap/{tap_type}/{amount}
```

| Tap Type (Integer) | Description     |
|--------------------|-----------------|
| 1                  | still water     |
| 2                  | medium water    |
| 3                  | sparkling water |

The amount is an integer in milliliters in steps of 50ml. The minimum amount is 50ml and the maximum is 2000ml.

You need to include the `API_KEY` in the header or as a query parameter to use the API.
The key is called `API_KEY` and the value is the one specified in the `settings.json` file.

## Disclaimer
This API is not officially supported by Grohe and may break at any time.  
The API is ment to be used on a local network and is not meant to be exposed to the internet.
There are no security measures in place to prevent unauthorized access to the API other than the API key.  
Use at your own risk.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
* [FlorianSW](https://github.com/FlorianSW/grohe-ondus-api-java) for his work on the Java Grohe IOT API. His Project inspired me to start working on this API.

## Contact
If you have any questions or suggestions, feel free to contact me via GitHub or create an issue if you have a problem, find a bug or have a feature request.
