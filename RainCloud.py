#!/usr/bin/python

# RainCloud Umbrella Minder by Jeremy Blum
# Copyright 2014 Jeremy Blum, Blum Idea Labs, LLC.
# http://www.jeremyblum.com
# File: RainCloud.py
# License: GPL v3 (http://www.gnu.org/licenses/gpl.html)

#Import needed libraries
import sys, ConfigParser, datetime, pywapi, requests, json

#Read configuration file
config = ConfigParser.ConfigParser()
config.read("config.ini")

#Main program execution
def main():
        #Let's get today's weather forecast!
        print "Checking the weather..."
        forecast_date = datetime.date.today()
        weekday = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        locations = [zipcode for zipcode in config.get('Location', weekday[forecast_date.weekday()]).split(', ')]
        activate = False
        for zipcode in locations:
                chance_precip = getForecast(zipcode)
                if chance_precip == -1:
                        print "Could not get forecast for zipcode " + zipcode + ". Skipping."
                else:
                        print "There is a " + str(chance_precip) + "% chance of rain in zipcode " + zipcode + " today.",
                        if chance_precip >= int(config.get('Preferences','threshold')):
                                print "[Above threshold of " + config.get('Preferences','threshold') + "%]"
                                activate = True;
                        else:
                                print "[Below threshold of " + config.get('Preferences','threshold') + "%]"
        if activate:
                print "You should bring an umbrella today."
                sys.stdout.write("Making sure RainCloud is enabled...")
        else:
                print "You don't need an umbrella today."
                sys.stdout.write("Making sure RainCloud is disabled...")
        [success, code, reason] = setOutput(activate)
        if success:
                print "Success!"
        else:
                #TODO: The API currently returns an HTTP 200, even when the device is disconnected from power. I need to find a way to detect this.
                print "Failed!"
                print "An Error " + str(code) + " was thrown when trying to command cloud module " + config.get('CloudModule', 'id') + "."
                print "Error Details: " + reason

#Sets the output State of the cloud bit. Stays set to this value until another command is issued.
#state = True or False
#Returns success (True/False), Status Code, and Status Reason 
def setOutput(state):
        url = "http://api-http.littlebitscloud.cc/devices/" + config.get('CloudModule', 'id') + "/output"
        headers = {'Authorization' : 'Bearer ' + config.get('CloudModule', 'token'),
                   'Accept'        : 'application/vnd.littlebits.v2+json'}
        if state == True:
                data = {'duration_ms':'-1'} #Turns output on indefinitely
        else:
                #Note: This is a hack. I should be setting the 'amount' variable to 0 in the payload,
                #      but the API is refusing calls to that variable.
                #      As a result, the light will blink for a millisecond if it is already off, and should stay off.
                data = {'duration_ms':'1'}  #Turn output off indefinitely
        
        r = requests.post(url, data=json.dumps(data), headers=headers)
        [success, code, reason] = [r.status_code == requests.codes.ok, r.status_code, r.reason]
        return [success, code, reason]

#Accepts a zipcode (string) as an argument, and returns today's chance of rain for that location as an int
def getForecast(zipcode):
        #TODO: I'm notatisfied with the accuracy of this. Switch it to the Darksky Forecast API: https://developer.forecast.io/docs/forecast
        weathercom = pywapi.get_weather_from_weather_com(zipcode)
        if weathercom.has_key('forecasts'):
                if weathercom['forecasts'][0].has_key('day'):
                        #TODO: Accuracy of this may be suspect. See issue: https://code.google.com/p/python-weather-api/issues/detail?id=38&thanks=38&ts=1403501545 
                        chance_precip = weathercom['forecasts'][0]['day']['chance_precip']
                else:
                        chance_precip = weathercom['forecasts'][0]['night']['chance_precip']
                return int(chance_precip)
        else:
                return -1

#Run the Main funtion when this python script is executed
if __name__ == '__main__':
  main()
