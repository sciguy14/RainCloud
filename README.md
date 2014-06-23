Getting Setup
=============
What you'll need
----------------
* Some LittleBits!
    * Cloud Module
	* Micro USB Power Bit
	* Force Sensor Bit
	* EL Wire Bit
* An always on Linux Machine. This can be a Raspberry Pi, a server in a remote data center, or anything in between. This instructions assume a debian-based distro, like ubuntu.

Prepare the Configuration File
------------------------------
* Rename "config_sample.ini" to "config.ini".
* Set The values in the "Preferences" and "Location" sections. You'll change the "CloudModule" section in the next steps.

Setup your LittleBits Account, and your Cloud Module
----------------------------------------------------
* Visit [http://littlebits.cc/cloudstart] and follow the instructions to setup the module.
* Set an easily recognizable, unique label for your cloud module.

Ensure json_pp is installed to make JSON outputs more readable
--------------------------------------------------------------
* sudo apt-get install libjson-pp-perl

Set your Authorization Token and Device ID
------------------------------------------
* Follow these instructions [http://developer.littlebitscloud.cc/access] to locate your access token.
* Specify your access token in the config.ini file.
* Open up a terminal and enter this command, replacing TOKEN with actual token value that you just copied into config.ini. If you chose not to install jsonpp, omit the pipe at the end of this command:  curl -XGET -H "Authorization: Bearer TOKEN" -H "Accept: application/vnd.littlebits.v2+json" http://api-http.littlebitscloud.cc/devices | json_pp
* Find the cloud module specified by your unique label, and add the "id" field output into the config.ini file.

Install the Python Preqrequistes
--------------------------------
* Install Python 2.7 if don't already have it installed: sudo apt-get install python2.7
* Install Python PIP if you haven't already: sudo apt-get install python-dev python-pip
* Instal the Python Requests Library: sudo pip install requests
* Install the Python Weather API Library: 
    * wget https://launchpad.net/python-weather-api/trunk/0.3.8/+download/pywapi-0.3.8.tar.gz
    * tar -zxvf pywapi-0.3.8.tar.gz
    * rm pywapi-0.3.8.tar.gz
    * cd pywapi-0.3.8
    * python setup.py build

TODO: Complete this documentation
Git clone my repo
make the program executable: chmod 755 RainCloud.py
Setup a cron job

License
=======
This work is licensed under the [GNU GPL v3](http://www.gnu.org/licenses/gpl.html).
Please share improvements or remixes with the community, and attribute me (Jeremy Blum, <http://www.jeremyblum.com>) when reusing portions of my code.


