# HTTP Tap Control API for Grohe Blue Devices
Use this API to dispense water from your Grohe Blue device.
The API uses the Grohe IOT API which is used by the Grohe Blue app.
The API is not publicly documented and may change at any time.

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
To use the API you need to create a `settings.json` file in the root directory of the project.
Feel free to use the `settings_example.json` file as a template.

Under `CREDENTIALS` you need to enter your Grohe Blue credentials.
The Sections `SERVER` and `API` are used to configure the API that will be started.


| :exclamation:  The `API_KEY` under `API` has to be unique and secure! |
|-----------------------------------------------------------------------|
Otherwise, anyone with access to the API can use it to dispense water from your Grohe Blue device.

You will also need to enter device information about your Grohe Blue device under the `DEVICE` section.
You can obtain this information by following the instructions in this [thread](https://github.com/FlorianSW/grohe-ondus-api-java/issues/12).
An automated script to obtain this information is planned.

## Usage
To start the API, run the following command:
```bash
python3 main.py
```
Currently, the API only supports the following endpoint:
```
GET /tap/{tap_type}/{amount}
```

| Tap Type (Integer) | Description     |
|--------------------|-----------------|
| 1                  | still water     |
| 2                  | medium water    |
| 3                  | sparkling water |

The amount is an integer in milliliters in steps of 50ml. The minimum amount is 50ml and the maximum is 2000ml.

## Disclaimer
This API is not officially supported by Grohe and may break at any time.
Use at your own risk.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
* [FlorianSW](https://github.com/FlorianSW/grohe-ondus-api-java) for his work on the Java Grohe IOT API. His Project inspired me to start working on this API.

## Contact
If you have any questions or suggestions, feel free to contact me via GitHub or create an issue if you have a problem, find a bug or have a feature request.