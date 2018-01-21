#!/usr/bin/python
""" clock7.py
	andyt wake up light alarm clock using various hardware.
	Works with slice of pi (slice == True).
	Works with ledborg.
"""

import time
import os, sys
import logging
import datetime
import alarmtime	# my module
board = 'bertie'
if board == 'slice':
	import gpio			# my module
elif board == 'ledborg':
	import ledborg as gpio	# alternative led solution
elif board == 'uoled':
	import uoled
elif board == 'blinkt':
	import blinktcontrol
elif board == 'bertie':
	import gpio
	import oled1
else:
	print "Error: board type not specified"
	sys.exit()
	
DISPLAY_CONNECTED = True
LOGFILE = '/home/pi/master/log/clock7.log'
TIMEOUT = 10		# seconds
STEPTIME = 30
HOLDTIME = 2000					# replaced by alarmtime value, which is read from file

class AlarmClock():
	"""Class to manage the alarmclock"""
	
	def __init__(self, board = 'bertie'):
		print "main:- Clock7.5 - alarm clock code for bertie."
		print 'Board selected:', board
		if board == 'slice':
			self.myGpio=gpio.gpio(board)
		elif board == 'ledborg':
			self.myGpio=gpio.Ledborg()
		elif board == 'blinkt':
			self.myGpio = blinktcontrol.Blinktcontrol()
		elif board == 'bertie':
			self.myGpio = gpio.gpio(board)

		# start one-shot timer
		self.last_set = datetime.datetime.now()

		addr = '0'
	#	addr = myGpio.get_ip_address()
		if addr is not '0':
			last_byte = addr.split('.')[3]
			print 'IP: ',addr,last_byte
			logging.info('IP address: '+addr)
			self.myGpio.writeleds(last_byte)
		else:
			logging.info('Zero IP address')
		self.myGpio.sequenceleds()
		self.myAlarmTime=alarmtime.AlarmTime()
		holdtime = self.myAlarmTime.return_holdtime()
		self.myDisplay = oled1.Oled()
		self.myDisplay.writerow(2, 'Alarmtime starting')
		string = "Alarm: %02d:%02d        " % (self.myAlarmTime.alarmhour,self.myAlarmTime.alarmminute)
		self.myDisplay.writerow(2, string)	
		self.main_loop()
			
	def main_loop(self):
		print 'Entering main loop'
		while True:
			t = time.strftime("%H:%M:%S")
			self.myDisplay.writerow(1, '   '+t+'       ')
			if self.check_screen_timer() == True:
				t = 'Alarm:'+self.myAlarmTime.read()+'      '
			else:
				t = "                     "
			self.myDisplay.writerow(2, t)		
			if(self.myAlarmTime.check()):
				self.myGpio.sequenceleds(STEPTIME, HOLDTIME)		# this is the alarm
			time.sleep(1)									# check every second

	def check_screen_timer(self):
		# one shot timer. True if still running.
		now = datetime.datetime.now()
		if now - self.last_set > datetime.timedelta(seconds=TIMEOUT):
			return(False)
		return(True)
	
if __name__ == "__main__":
	'''	clock6 main routine
		Sets up the logging and constants, before calling ...
	'''
#	logging.basicConfig(format='%(levelname)s:%(message)s',
	logging.basicConfig(
						filename=LOGFILE,
						filemode='w',
						level=logging.INFO)	#filemode means that we do not append anymore
#	Default level is warning, level=logging.INFO log lots, level=logging.DEBUG log everything
	logging.warning(datetime.datetime.now().strftime('%d %b %H:%M')+". Running clock7 class as a standalone app")
	myAlarmclock = AlarmClock()
	
	