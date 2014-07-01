Getting Setup
=============
What you'll need
----------------
* Some LittleBits!
    * Cloud Module
	* Micro USB Power Bit
	* Force Sensor Bit
	* EL Wire Bit
* An always on Linux Machine. This can be a Raspberry Pi, a server in a remote data center, or anything in between. These instructions assume a debian-based distro, like ubuntu.

Prepare the Configuration File
------------------------------
* Rename "config_sample.ini" to "config.ini".
* Add lat/lng coordinates in the "Location" section, using the format shown. You can determine the lat/lng of your location by searching for it in Google Maps, and copying the latitude and longitude from the resulting search URL. For each day of the week, include a list of the palces where you'll be. This is usually your home/work coordinates on weekdays, and your home coordinates on weekends. The script will check for chances of precipitation at those locations.
* Set the threshold value in the "Preferences" section based on when you want the RainCloud to light up.

Setup your LittleBits CloudMole, and set its Token/Device ID
------------------------------------------------------------
* Visit [http://littlebits.cc/cloudstart] and follow the instructions to setup the module.
* Set an easily recognizable, unique label for your cloud module.
* Ensure json_pp is install to make the next steps easier: sudo apt-get install libjson-pp-perl
* Follow these instructions [http://developer.littlebitscloud.cc/access] to locate your access token.
* Specify your access token in the config.ini file.
* Open up a terminal and enter this command, replacing TOKEN with actual token value that you just copied into config.ini:  curl -XGET -H "Authorization: Bearer TOKEN" -H "Accept: application/vnd.littlebits.v2+json" http://api-http.littlebitscloud.cc/devices | json_pp
* Find the cloud module specified by your unique label, and add the "id" field output into the config.ini file.

Set your Forecast.io API Key
----------------------------
* Visit https://developer.forecast.io/register and sign up for an account
* Copy your API from the bottom of the page into the config.ini file

Install the Python Preqrequistes
--------------------------------
* Install Python 2.7 if don't already have it installed: sudo apt-get install python2.7
* Install Python PIP if you haven't already: sudo apt-get install python-dev python-pip
* Install the Python Requests Library: sudo pip install requests
* Install the Forecast.IO Library: sudo pip install python-forecastio

Setting up the file
-------------------
* Copy the file to your server
* Make it executable: chmod 755 RainCloud.py
* Setup a Cronjob: crontab -e, Add: */10 * * * *   /PATH_TO_PYTHON_FILE/RainCloud.py

Optional: Setup Subscription Service
------------------------------------
* Populate appropriate fields in config file
* run ./RainCloud.py - s, you only need to do it once
* It will now send a post request to this server when ever the umbrella is inserted or removed
* Launch a continously running web service to handle those incoming post requests
* ./RainCloud.py -l


TODO: Complete this documentation
Git clone my repo

License
=======
This work is licensed under the [GNU GPL v3](http://www.gnu.org/licenses/gpl.html).
Please share improvements or remixes with the community, and attribute me (Jeremy Blum, <http://www.jeremyblum.com>) when reusing portions of my code.


