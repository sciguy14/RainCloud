#!/usr/bin/python

# RainCloud Umbrella Minder by Jeremy Blum
# Copyright 2014 Jeremy Blum, Blum Idea Labs, LLC.
# http://www.jeremyblum.com
# File: RainCloud.py
# License: GPL v3 (http://www.gnu.org/licenses/gpl.html)

#Import needed libraries
import sys, ConfigParser, datetime, forecastio, requests, json, ast, argparse

#Read configuration file
config = ConfigParser.ConfigParser()
config.read("config.ini")

#Main program execution
def main():

        #Perform Preflight Checks 
	#TODO: Confirm valid values in the config file

        #Parse optional override argument
        parser = argparse.ArgumentParser(description='Controller for the RainCloud Umbrella Minder')
        parser.add_argument('-o','--override', help='Use "-o on" or "-o off" to manually override the current setting,\
                                                      and control the RainCloud manually. Note, if you\'re running\
                                                      this as a cron job, your manual setting may quickly overriden.', required=False)
        args = vars(parser.parse_args())

        #Trigger Override
        if args.has_key('override') and args['override'] is not None:
                if args['override'] == "on":
                        sys.stdout.write("Override enabled. Turning on RainCloud...")
                        activate = True
                elif args['override'] == "off":
                        sys.stdout.write("Override enabled. Turning off RainCloud...")
                        activate = False
                else:
                        print "Invalid override option. Valid options are 'on' or 'off'. Exiting."
                        exit()
        #No override triggered. Let's get today's weather forecast!
        else:
                print "Checking the weather..."
                forecast_date = datetime.date.today()
                weekday = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                locations = [location for location in config.get('Location', weekday[forecast_date.weekday()]).split(';')]
                activate = False
                for location in locations:
                        latlng = ast.literal_eval(location)
                        chance_precip = getForecast(latlng[0], latlng[1])
                        if chance_precip == -1:
                                print "Could not get forecast for location " + location + ". Skipping."
                        else:
                                print "There is a " + str(chance_precip) + "% chance of rain at location " + location + " over the next " + config.get('Preferences', 'look_ahead_hours') + " hours.",
                                if chance_precip >= int(config.get('Preferences','threshold')):
                                        print "(Above threshold of " + config.get('Preferences','threshold') + "%)"
                                        activate = True;
                                else:
                                        print "(Below threshold of " + config.get('Preferences','threshold') + "%)"
                if activate:
                        print "You should bring an umbrella today."
                        sys.stdout.write("Making sure RainCloud is enabled...")
                else:
                        print "You don't need an umbrella today."
                        sys.stdout.write("Making sure RainCloud is disabled...")

        #Use the LittleBits API to setup the RainCloud
	[success, code, reason] = setOutput(activate)
	if success:
		print "Success!"
	else:
		#TODO: The API currently returns an HTTP 200, even when the device is disconnected from power. LittleBits is aware of this limitation, and is investigating what HTTP Status codes could be used to convey this error, if it occurs.
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
		data = {'percent'     :'100', #Full Intensity
				'duration_ms':'-1'}  #Turns output on indefinitely
	else:
		data = {'percent':'0'}  #Turn output off indefinitely
        
	r = requests.post(url, data=json.dumps(data), headers=headers)
	[success, code, reason] = [r.status_code == requests.codes.ok, r.status_code, r.reason]
	return [success, code, reason]

#Accepts a latitude and longitude (floats), and returns the worst-case chance of rain over the next 12 hours
#Returned value is a percentage from 0 to 100% (inclusive) represented as an int
#A Value of -1 is returned if a chance of precipitation could not be determined
def getForecast(lat,lng):
	forecast = forecastio.load_forecast(config.get('ForecastIO', 'api_key'), lat, lng)
	byHour = forecast.hourly()
	worst_case_chance_precip = -1
	for hourlyData in byHour.data[0:int(config.get('Preferences', 'look_ahead_hours'))]:
		try:
			hourly_chance_precip = int(float(hourlyData.precipProbability)*100.0)
			if hourly_chance_precip > worst_case_chance_precip:
				worst_case_chance_precip = hourly_chance_precip
		except AttributeError:
			worst_case_chance_precip = -1
	return worst_case_chance_precip

#Run the Main funtion when this python script is executed
if __name__ == '__main__':
	main()
