#!/usr/bin/python
""" clock7.py
	andyt wake up light alarm clock using various hardware.
	Works with slice of pi (slice == True).
	Works with ledborg.
	Works with bertie.
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
TIMEOUT = 5		# seconds
STEPTIME = 10
# HOLDTIME = 2000					# replaced by alarmtime value, which is read from file
HOLDTIME = 20					# replaced by alarmtime value, which is read from file
HOLDLEDPOSITION = 4
FILEWRITEDELAY = 30

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

		self.start_screen_timer()
		self.last_led_time = datetime.datetime.now()
		
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
		self.myAlarm=alarmtime.AlarmTime()
		holdtime = self.myAlarm.return_holdtime()
		self.myDisplay = oled1.Oled()
		self.myDisplay.writerow(1, 'Initialising')
		self.myDisplay.writerow(2, 'Alarmtime starting')
		self.file_write_needed = False
#		self.myGpio.setupcallbacks()			# cannot get this to initialise right now?
		self.main_loop()
		
	def main_loop(self):
		print 'Entering main loop'
		self.counter = 0
		self.alarm_running = False
		while True:
			self.update_display()
			self.write_alarm_times_file()
			if self.alarm_running:
				self.next_led()
			else:
				if(self.myAlarm.check()):
					self.alarm_running = True
					self.next_led()
			time.sleep(1)									# check every second

	def next_led(self):
		now = datetime.datetime.now()
		if self.counter == HOLDLEDPOSITION:			# all on, so need to hold here
			delta_time = HOLDTIME
		else:
			delta_time = STEPTIME
		if now - self.last_led_time > datetime.timedelta(seconds = delta_time):
			self.myDisplay.writerow(2, 'Alarm started:'+str(self.counter))
			self.last_led_time = now
			self.myGpio.alarm_sequence(self.counter)
			self.counter += 1
			if self.counter == 7:
				self.counter = 0
				self.alarm_running = False
		return(0)
		
	def write_alarm_times_file(self):
		if self.file_write_needed:
			now = datetime.datetime.now()
			if now - self.last_set > datetime.timedelta(seconds=FILEWRITEDELAY):
				print "Writing alarm time file"
				self.myAlarm.write()
				self.file_write_needed = False
		return(0)
		
	def update_display(self):
		self.myDisplay.writerow(1, time.strftime("   %H:%M:%S   "))
		if self.button_pressed():
			self.myDisplay.writerow(2, 'Alarm:'+self.myAlarm.alarmtime_string()+'      ')
			self.start_screen_timer()
			return(0)
		if self.screen_timedout() == False:
			self.myDisplay.writerow(2, 'Alarm:'+self.myAlarm.alarmtime_string()+'     ')
			return(0)
		if self.alarm_running == False:
			self.myDisplay.writerow(2, "                     ")		
		return(0)
	
	def button_pressed(self):
		if self.myGpio.button1() == 0:
			self.start_screen_timer()		# start one-shot timer
			return(True)
		if self.myGpio.button2() == 0:
			self.start_screen_timer()		# start one-shot timer
			return(True)
		if self.myGpio.button3() == 0:
			self.myAlarm.increment_alarmhour()
			self.file_write_needed = True
			return(True)
		if self.myGpio.button4() == 0:
			self.myAlarm.increment_alarmminute()
			self.file_write_needed = True
			return(True)
		return(False)
	
	def start_screen_timer(self):
		self.last_set = datetime.datetime.now()
		return(0)
		
	def screen_timedout(self):
		# one shot timer. True if still running.
		now = datetime.datetime.now()
		if now - self.last_set > datetime.timedelta(seconds=TIMEOUT):
			return(True)
		return(False)
	
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
	
	