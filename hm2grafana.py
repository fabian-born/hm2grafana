#!/usr/bin/python
from xml.dom import minidom
import urllib
import time,thread
import sys,getopt
import configparser,logging
import socket
import logging

##### variable definition ####
global timestamp
timestamp = int(time.time())
LOG_FILENAME = 'log/hm2grafana.log'
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename='/home/fabian/hm/hm2grafana/log/hm2grafana.log', filemode='w')


def send2graphite(graphitepath,value,timestamp):
    sock = socket.socket()
    graphiteserver = str(config['grafana']['graphiteserver'])
    graphiteport = int(config['grafana']['graphiteport'])
    sock.connect(( graphiteserver, graphiteport ))
    sock.send("%s %s %d\n" % (graphitepath, value, timestamp))
    sock.close()

def sonderzeichen(eing):
   a = repr(eing)
   a = a.replace("\\xe4","")
   a = a.replace("\\xfc","ue")
   a = a.replace("\\xf6","")
   a = a[1:]
   a = a.replace("\'","")      
   a = str(a)
   return a

def readDevice(deviceID,deviceName):
   # open DEVICE URL: 
   import socket
   deviceurl = "http://" + config['general']['ccu'] + "/config/xmlapi/state.cgi?device_id=" + deviceID
   dusocket = urllib.urlopen(deviceurl)
   xmldevices = minidom.parse(dusocket)
   dusocket.close()
   datapoints = xmldevices.getElementsByTagName('datapoint')
   devname=sonderzeichen(deviceName)
   logging.info("Read Device from URL %s" % deviceurl) 
   for datapoint in datapoints:
   	if datapoint.attributes['valuetype'].value == '4':
           grafanapath = grafanaroot + "." + devname.replace(" ","_") + "." + datapoint.attributes['type'].value
	   if config['general']['loglevel']  == "DEBUG":
		logging.debug("Device Information")
		logging.debug("============================")
		logging.debug("Device Name: ")
	   value = datapoint.attributes['value'].value
	   if value != '':
		send2graphite(grafanapath,value,timestamp)
#	print timestamp


def getRoomlist():
   roomurl = "http://" + config['general']['ccu'] + "/config/xmlapi/rooms.cgi?device_id=" + deviceID
   roomsocket = urllib.urlopen(roomurl)
   xmlroom = minidom.parse(roomsocket)
   roomsocket.close()
   return xmlroom

def getDevicesinRoom(roomName,roomID):
   roomurl = "http://" + config['general']['ccu'] + "/config/xmlapi/rooms.cgi?device_id=" + deviceID
   roomsocket = urllib.urlopen(roomurl)
   xmlroom = minidom.parse(roomsocket)
   roomsocket.close()   


def main(argv):
   global config
   global grafanaroot
   inputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hc:",["configfile="])
   except getopt.GetoptError:
      print 'test.py -c <configfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -c <configfile>'
         sys.exit()
      elif opt in ("-c", "--configfile"):
         inputfile = arg
   # print 'Input file is ', inputfile

   logging.info('*********************************************')
   logging.info('* hm2grafana                                *')
   logging.info('*********************************************') 
   logging.info('Loading ConfigFile %s',inputfile)
   config = configparser.ConfigParser()
   config.read(inputfile)
   if not config['general']['loglevel']:
	config['general']['loglevel'] = "INFO"
   
   apiurl = "http://" + config['general']['ccu'] + "/config/xmlapi/devicelist.cgi"
   usock = urllib.urlopen(apiurl) 
   grafanaroot=config['grafana']['grafanaroot']
   xmldoc = minidom.parse(usock)                              
   usock.close()
   devices = xmldoc.getElementsByTagName('device')
   for device in devices:
	dev_name = device.attributes['name'].value
	dev_iseid = device.attributes['ise_id'].value

	readDevice( dev_iseid,dev_name )
	#	print " " 
	#	print "  %s" % devname
	#	print "		===== ID: %s =====" % dev_iseid
#		url = "http://" + config['general']['ccu'] + "/config/xmlapi/state.cgi?device_id=" + dev_iseid
	#	print "		URL: %s" % url
#		usock2 = urllib.urlopen(url)
##		xmldoc2 = minidom.parse(usock2)
##		usock2.close()
##		datapoints = xmldoc2.getElementsByTagName('datapoint')
##		devname=sonderzeichen(devname)
##		for datapoint in datapoints:
##			if datapoint.attributes['valuetype'].value == '4':
##				grafanapath = grafanaroot + "." + devname.replace(" ","_") + "." + datapoint.attributes['type'].value 
		#			print grafanapath
				#	collect_metric(grafanapath, datapoint.attributes['value'].value, timestamp)
		# print xmldoc.toxml() 

if __name__ == "__main__":
    global config
    import sys
    main(sys.argv[1:])
