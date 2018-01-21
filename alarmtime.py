#!/usr/bin/python
""" alarmtime.py

	"""
	
import time
import datetime
import logging
import oled1

ALARMTIMEFILE = '/home/pi/master/bertie/alarmtime.txt'			# change this to relative dir?
LOGFILE = '/home/pi/master/log/alarmtime.log'
DISPLAY_CONNECTED = True

class AlarmTime():
	"""Class to manage the time for the alarm"""
	
	def __init__(self):
		print 'Running alarmtime'
		self.logger = logging.getLogger(__name__)
		self.logger.info("Initialising alarm time")
		a=0 # just to fix the formatting
		self.alarmhour=6
		self.alarmminute=20
		self.wealarmhour=7
		self.wealarmminute=00
		self.holdtime = 2000			# seconds
		self.read()
		print 'Finished initialising'
		
	def read(self):
		self.logger.info("Reading alarm time")
		try:
			file=open(ALARMTIMEFILE,'r')
			line1=file.readline()
			line2=file.readline()
			self.holdtime = int(file.readline())
			file.close()
			a,b = line1.split(":")
			self.alarmhour=int(a)
			self.alarmminute = int(b)
			a,b = line2.split(":")
			self.wealarmhour=int(a)
			self.wealarmminute = int(b)
		except:
			self.logger.warning("Failed to open alarmtime file, using defaults.")
		# select which is correct time to return as the next alarm time.
		timenow=list(time.localtime())
		day=timenow[6]
		if day < 5:				# weekday timings		
			string = "%02d:%02d" % (self.alarmhour,self.alarmminute)
		else:
			string = "%02d:%02d we" % (self.wealarmhour,self.wealarmminute)		
		self.logger.info("Weekday alarm time: %02d:%02d" % (self.alarmhour,self.alarmminute))
		self.logger.info("Weekend alarm time: %02d:%02d" % (self.wealarmhour,self.wealarmminute))
		self.logger.info("Hold time: %02d" % (self.holdtime))
		return(string)
		
	def return_holdtime(self):
		return(self.holdtime)
		
	def check(self):
		''' Check whether alarm should go off and return that state.'''
		self.logger.info("Checking alarm")
		self.read()					# re-read the file in case it has been updated.
		timenow=list(time.localtime())
		hour=timenow[3]
		minute=timenow[4] 
		day=timenow[6]
		if day < 5:				# weekday timings
			if ((hour == self.alarmhour) and (minute == self.alarmminute)):
				self.logger.warning("Alarm going off")
				print "Alarm going off"
				return(True)
			else:
				return(False)
		else:					# weekend timings
			if ((hour == self.wealarmhour) and (minute == self.wealarmminute)):
				self.logger.warning("Alarm going off")
				print "Alarm going off"
				return(True)
			else:
				return(False)
		

if __name__ == "__main__":
	'''	alarmtime main routine
		Sets up the logging and constants, before calling ...
	'''
#	logging.basicConfig(format='%(levelname)s:%(message)s',
	logging.basicConfig(
						filename=LOGFILE,
						filemode='w',
						level=logging.INFO)	#filemode means that we do not append anymore
#	Default level is warning, level=logging.INFO log lots, level=logging.DEBUG log everything
	logging.warning(datetime.datetime.now().strftime('%d %b %H:%M')+". Running alarmtime class as a standalone app")

	myAlarmTime = AlarmTime()
	if DISPLAY_CONNECTED == True:
		print 'setting display'
		myDisplay = oled1.Oled()
		myDisplay.writerow(2, 'Alarmtime starting')
		myAlarmTime.read()
		string = "Alarm: %02d:%02d        " % (myAlarmTime.alarmhour,myAlarmTime.alarmminute)
		myDisplay.writerow(2, string)		
	while(True):
		t = time.strftime("%H:%M:%S")
		myDisplay.writerow(1, '   '+t+'       ')
		myAlarmTime.check()
		time.sleep(1)
	
	