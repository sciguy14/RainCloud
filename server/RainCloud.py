#!/usr/bin/python

# RainCloud Umbrella Minder by Jeremy Blum
# Copyright 2014 Jeremy Blum, Blum Idea Labs, LLC.
# http://www.jeremyblum.com
# File: RainCloud.py
# License: GPL v3 (http://www.gnu.org/licenses/gpl.html)

#Import needed libraries
import sys, ConfigParser, datetime, forecastio, requests, json, ast, argparse, urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

#Read configuration file
config = ConfigParser.ConfigParser()
config.read("config.ini")

#Main program execution
def main():

        #Perform Preflight Checks 
	#TODO: Confirm valid values in the config file

        #Parse optional override argument and determine if the script is launching in listening mode
        parser = argparse.ArgumentParser(description='Controller for the RainCloud Umbrella Minder. Omit arguments to run normal update routine.')
        parser.add_argument('-o','--override', help='Use "-o on" or "-o off" to manually override the current setting,\
                                                     and control the RainCloud manually. Note, if you\'re running\
                                                     this as a cron job, your manual setting may be quickly overriden.', required=False)
        parser.add_argument('-l','--listen', help='Launch in continuous listening mode to run\
                                                   the listening service for the force sensor.', required=False, action='store_true')
        parser.add_argument('-s','--setup', help='Sets up your Cloud Module to send its input state to this server.\
                                                  You only need to run this once.', required=False, action='store_true')
        args = vars(parser.parse_args())

        #Can only be in one of override, listen, or setup modes
        args_count = 0
        if args.has_key('override') and args['override']:
                args_count = args_count + 1
        if args.has_key('listen') and args['listen']:
                args_count = args_count + 1
        if args.has_key('setup') and args['setup']:
                args_count = args_count +1
        if args_count > 1:
                print "You can only specify one of 'override', 'listen', or 'setup' modes at a time. Exiting."

        #Setup Mode (Create LittleBits Subscription service)
        elif args.has_key('setup') and args['setup']:
                #Delete existing suscriptions to this server
                sys.stdout.write("Deleting existing publishing to " + config.get('Server', 'FQDN') + ":" + config.get('Server', 'port') + "...")
                [success, code, reason] = deleteSubscription()
                if success:
                        print "Success!"
                else:
                        print "Failed!"
                        print "An Error " + str(code) + " was thrown when trying to delete existing subscriptions for cloud module " + config.get('CloudModule', 'id') + "."
                        print "Error Details: " + reason
                #Use the LittleBits API to setup the subscriptions
                sys.stdout.write("Subscribing " + config.get('Server', 'FQDN') + ":" + config.get('Server', 'port') + " to ignite & release triggers...")
                [success, code, reason] = setSubscription()
                if success:
                        print "Success!"
                else:
                        print "Failed!"
                        print "An Error " + str(code) + " was thrown when trying to configure subscriptions for cloud module " + config.get('CloudModule', 'id') + "."
                        print "Error Details: " + reason

        #Listening Mode (Start server)
        elif args.has_key('listen') and args['listen']:
                try:
                        server = HTTPServer(('',int(config.get('Server', 'port'))),customHTTPServer)
                        print "Server launched on port " + config.get('Server', 'port') + " to listen for data from the RainCloud..."
                        server.serve_forever()
                except KeyboardInterrupt:
                        server.socket.close() 
        
        #Not listening or setup mode (Override or Normal operation)
        else:
                #Trigger Override
                if args.has_key('override') and args['override'] is not None:
                        if args['override'] == "on":
                                sys.stdout.write("Override enabled. ")
                                activate = True
                        elif args['override'] == "off":
                                sys.stdout.write("Override enabled. ")
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
                        with open("forecast.txt", "w") as f:
                                f.write("yes\n")
                        sys.stdout.write("Making sure RainCloud is enabled...")
                else:
                        print "You don't need an umbrella today."
                        with open("forecast.txt", "w") as f:
                                f.write("no\n")
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
		data = {'percent'     : '100', #Full Intensity
		        'duration_ms' : '-1'}  #Turns output on indefinitely
	else:
		data = {'percent':'0'}  #Turn output off indefinitely
        
	r = requests.post(url, data=json.dumps(data), headers=headers)
	[success, code, reason] = [r.status_code == requests.codes.ok, r.status_code, r.reason]
	return [success, code, reason]

#Deletes an existing Subscription to our server. Necessary if we need to reconfigure for some reason.
def deleteSubscription():
        url = "https://api-http.littlebitscloud.cc/subscriptions"
        headers = {'Authorization' : 'Bearer ' + config.get('CloudModule', 'token'),
	           'Accept'        : 'application/vnd.littlebits.v2+json'}
        data = {'publisher_id'     :  config.get('CloudModule', 'id'),
                'subscriber_id'    : 'http://' + config.get('Server', 'FQDN') + ":" + config.get('Server', 'port')}
        r = requests.delete(url, data=json.dumps(data), headers=headers)
        [success, code, reason] = [r.status_code == requests.codes.ok, r.status_code, r.reason]
	return [success, code, reason]

#Subscribes our server to input events for our cloud bit
#Returns sucess (True/False), Status Code, and Status Reason
def setSubscription():
        url = "https://api-http.littlebitscloud.cc/subscriptions"
        headers = {'Authorization' : 'Bearer ' + config.get('CloudModule', 'token'),
	           'Accept'        : 'application/vnd.littlebits.v2+json'}
        data = {'publisher_id'     :  config.get('CloudModule', 'id'),
                'subscriber_id'    : 'http://' + config.get('Server', 'FQDN') + ":" + config.get('Server', 'port'),
                'publisher_events' : ['amplitude:delta:ignite', 'amplitude:delta:release']}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        [success, code, reason] = [r.status_code == requests.codes.ok, r.status_code, r.reason]
        #201 is actually a success code, so this handles that.
        if code == 201:
                success = True
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

class customHTTPServer(BaseHTTPRequestHandler):
        #POSTS come exclusively from the Little Bits Cloud
        def do_POST(self):
                sys.stdout.write("POST Received...")
                length = int(self.headers.getheader('content-length'))
                postvars = urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)

                # Decode the POST data
                self.wfile.write(postvars)
                data = json.loads(postvars.keys()[0])
                if data['bit_id'] == config.get('CloudModule', 'id'):
                        self.send_response(200)
                        self.end_headers()
                        with open("state.txt", "w") as f:
                                f.write(data['payload']['level'] + "\n")
                        print "State set to " + data['payload']['level'] + "."
                else:
                        self.send_response(401)
                        self.end_headers()
                        print "Bit ID mismatch. Request denied."
                return
        #GETS come exclusively from 
        def do_GET(self):
                sys.stdout.write("GET Received...")
                getvars = urlparse.parse_qs(urlparse.urlparse(self.path).query)
                if getvars.has_key('key') and getvars['key'][0] == config.get('Server', 'key'):
                        print "The user has left the home."
                        self.send_response(200)
                        self.send_header("Content-type", "text/plain")
                        self.end_headers()
                        with open("state.txt") as f:
                                state_file = f.readlines()
                        with open("forecast.txt") as f:
                                forecast_file = f.readlines()
                        state = state_file[0].strip()
                        forecast = forecast_file[0].strip()
                        if state == "active" and forecast == "yes":
                                #Umbrella Left Behind, and it's going to rain!
                                print 'Umbrella needed, but left behind. Informing user.'
                                self.wfile.write('It\'s going to rain! Get your umbrella!')
                        elif state == "idle" and forecast == "yes":
                                #Umbrella taken, and it's going to rain!
                                print 'Umbrella needed, and taken by user. Nothing sent to user.'
                        else:
                                #It's not going to rain!
                                print 'No Rain today! Nothing sent to user'     
                else:
                        print "Key mismatch. Request denied."
                        self.send_response(401)
                        self.end_headers()
                return
                

#Run the Main funtion when this python script is executed
if __name__ == '__main__':
	main()
