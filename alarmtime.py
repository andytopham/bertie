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
		self.alarmhour=6
		self.alarmminute=20
		self.wealarmhour=7
		self.wealarmminute=00
		self.holdtime = 20			# seconds
		self.steptime = 5			# seconds
		self.read()
		print 'Finished initialising'
		
	def read(self):
		self.logger.info("Reading alarm time")
		try:
			file=open(ALARMTIMEFILE,'r')
			line1=file.readline()
			line2=file.readline()
			self.holdtime = int(file.readline())
			self.steptime = int(file.readline())
			file.close()
			a,b = line1.split(":")
			self.alarmhour=int(a)
			self.alarmminute = int(b)
			a,b = line2.split(":")
			self.wealarmhour=int(a)
			self.wealarmminute = int(b)
		except:
			self.logger.warning("Failed to open alarmtime file, using defaults.")
		self.logger.info("Weekday alarm time: "+self.alarmtime_string())
		self.logger.info("Weekend alarm time: "+self.alarmtime_string_we())
		self.logger.info("Hold time: {:02d}".format(self.holdtime))
		return(0)

	def write(self):
		self.logger.info("Writing alarm time")
		try:
			file=open(ALARMTIMEFILE,'w')
			file.write("{:02d}:{:02d}\n".format(self.alarmhour,self.alarmminute))
			file.write("{:02d}:{:02d}\n".format(self.wealarmhour,self.wealarmminute))
			file.write("{:04d}\n".format(self.holdtime))
			file.write("{:03d}".format(self.steptime))
			file.close()
		except:
			self.logger.warning("Failed to open alarmtime file for writing.")
			return(1)
		return(0)
						
	def alarmtime_string(self):
		return('{:02d}:{:02d}'.format(self.alarmhour, self.alarmminute))

	def alarmtime_string_we(self):
		return('{:02d}:{:02d}'.format(self.wealarmhour, self.wealarmminute))
		
	def increment_alarmhour(self):
		self.alarmhour += 1
		if self.alarmhour > 23:
			self.alarmhour = 0
		print 'New alarm time:',self.alarmtime_string()
		return(0)
		
	def increment_alarmminute(self):
		self.alarmminute += 1
		if self.alarmminute > 59:
			self.alarmminute = 0
		print 'New alarm time:',self.alarmtime_string()
		return(0)
		
	def check(self):
		''' Check whether alarm should go off and return that state.'''
		self.logger.info("Checking alarm")
#		self.read()					# re-read the file in case it has been updated.
		timenow=list(time.localtime())
		hour=timenow[3]
		minute=timenow[4] 
		day=timenow[6]
		day = 0 			# this is just for testing!!!!!!
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
	
	