#!/usr/bin/python
# gpio.py
# Control leds connected to gpio pins, typically via a slice of pi board.

import RPi.GPIO as GPIO
import time
import datetime
import socket, fcntl, struct
import logging
BERTIE_TEST = False
TEST_OUTPUT = True
WRITELEDSTATEENABLED = False
LEDSTATEFILE = './ledstate.txt'
LOGFILE = '/home/pi/master/log/gpio.log'

class gpio:
	'''A class containing ways to handle the RPi gpio. '''
	def __init__(self, board = 'bertie'):
		'''Initialise GPIO ports. '''
		self.logger = logging.getLogger(__name__)
		self.logger.info("Starting gpio class")
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		self.rpi_gpio_chk_function()	
		rev = GPIO.RPI_INFO['P1_REVISION']
		print 'RPi board revision:',str(rev)
		self.logger.info('RPi board revision:'+str(rev))
		self.logger.info('HAT type: '+board)
		if rev == 1:
			if board == 'slice':
				self.pins = [17,18,21,22,23,24,25,4]	# wiring pi numbering
			else:
				self.pins = [4,17,21,18,22,23,24,25]
		else:
			if board == 'slice':	# This array is the Slice of Pi pins: GP0-7
				self.pins = [17,18,27,22,23,24,25,4]	# wiring pi numbering
			else:
				self.pins = [4,17,27,18,22,23,24,25]	# rev 2 pinout
		if board == 'bertie':
			self.pins = [23,24,25]
			self.bertie_inputs = [17, 18, 27, 22] 
		GPIO.setup(self.pins, GPIO.OUT)		# can now set all pins as outputs in one statement by passing the array.
		self.logger.info('gpio initialised')

	def get_ip_address(self, ifname = 'wlan0'):
		self.logger.info('get_ip_address')
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,  # SIOCGIFADDR
				struct.pack('256s', ifname[:15]))[20:24])
		except:
			return('0')
			
	def rpi_gpio_chk_function(self):
		# Now updated to use BCM mode
		retstr = ''
		pin = 10		# 19
		GPIO.setmode(GPIO.BCM)
		func = GPIO.gpio_function(pin)
		if func == GPIO.SPI:
			print 'SPI enabled'
			retstr += 'SPI '
		else:
			print 'Warning: SPI not enabled!'
		pin = 2		# 3
		func = GPIO.gpio_function(pin)
		if func == GPIO.I2C:
			print 'I2C enabled'
			retstr += 'I2C '
		else:
			print 'Warning: I2C not enabled!'
		pin = 14 		# 8
		func = GPIO.gpio_function(pin)
		if func == GPIO.SERIAL:
			print 'Serial enabled'
			retstr += 'Serial '
		else:
			print 'Warning: Serial not enabled!'
		pin = 18 		# 12
		func = GPIO.gpio_function(pin)
		if func == GPIO.HARD_PWM:
			print 'PWM enabled'
			retstr += 'PWM '
		else:
			print 'Warning: PWM not enabled!'
		return(retstr)
	
	def writeledstate(self, lednumber, ledstate):
		''' Save the state of an led in the state file. '''
		if WRITELEDSTATEENABLED == False:
			return(1)
		self.logger.info('writeledstate')
		led = []
		try:
			file = open(LEDSTATEFILE,'r+')		# read and write
		except:
			file = open(LEDSTATEFILE,'w')		# if file does not exist
			file.write('0 0 0 0 0 0 0 0')
			file.close()
			file = open(LEDSTATEFILE,'r+')		# read and write	
		line = file.readline()
		led = line.split()
		led[lednumber] = ledstate
		file.seek(0)			# rewind file
		for i in range(8):
			file.write(str(led[i])+" ")
		file.close()
		return(0)
			
	def sequenceleds(self, delay=0.5, holdtime=0.5):
		'''The main led alarm sequence. Also, alternative test routine to be used with the clock3 slice of pi.'''
		self.logger.debug("def gpio sequenceleds")
		# Set all pins as outputs
		for i in range(len(self.pins)):
			GPIO.setup(self.pins[i], GPIO.OUT)
			GPIO.output(self.pins[i], GPIO.LOW)
		for i in range(len(self.pins)):
			time.sleep(delay)
			print "High:",self.pins[i]
			GPIO.output(self.pins[i], GPIO.HIGH)
			self.writeledstate(i,1)
		time.sleep(holdtime)
		for i in range(len(self.pins)):
			time.sleep(delay)
			print "Low:",self.pins[i]
			GPIO.output(self.pins[i], GPIO.LOW)
			self.writeledstate(i,0)
			
	def writeleds(self, write_byte, holdtime = 5):
		'''Write the last_byte value to the leds.'''
		self.logger.debug("def gpio writeleds")
		# Set all pins as outputs
		for i in range(len(self.pins)):
			GPIO.setup(self.pins[i], GPIO.OUT)
			GPIO.output(self.pins[i], GPIO.LOW)
		if write_byte == '0':
			self.flash_error()
		else:
			mask = 1
			test_byte = int(write_byte) & 255
			for i in range(len(self.pins)):
				if (test_byte & mask):
					print "Address High:",self.pins[i], 'mask ' , mask
					GPIO.output(self.pins[i], GPIO.HIGH)
					self.writeledstate(i,1)
				mask = mask * 2
			time.sleep(holdtime)
			self.off()
				
	def off(self):
		self.logger.info('gpio off')
		print 'All off'
		for i in range(len(self.pins)):
			GPIO.output(self.pins[i], GPIO.LOW)
			self.writeledstate(i,0)
	
	def flash_error(self):
		self.logger.info('gpio flash_error')
		for i in range(10):
			GPIO.output(self.pins[0], GPIO.HIGH)
			time.sleep(.5)
			GPIO.output(self.pins[0], GPIO.LOW)
			time.sleep(.5)
			
	def scan(self):
		# Continuously read the gpio input pins and print results.
		for i in range(len(self.pins)):
			GPIO.setup(self.pins[i],GPIO.IN, pull_up_down=GPIO.PUD_UP)
			print self.pins[i]," ",
		print
		while True:
			for i in range(len(self.pins)):
				print GPIO.input(self.pins[i]),"  ",
			print
			time.sleep(1)
			
	def bertie_test(self, delay = 1, holdtime = 1):
		for i in self.pins:
			GPIO.setup(i, GPIO.OUT)
			GPIO.output(i, GPIO.LOW)
		for i in self.pins:
			time.sleep(delay)
			print "High:",i
			GPIO.output(i, GPIO.HIGH)
			self.writeledstate(i,1)
		time.sleep(holdtime)
		for i in self.pins:
			time.sleep(delay)
			print "Low:",i
			GPIO.output(i, GPIO.LOW)
		for i in self.bertie_inputs:
			GPIO.setup(i,GPIO.IN, pull_up_down=GPIO.PUD_UP)
			print i," ",
		print
		return(0)
		
	def bertie_test_inputs(self):
		while True:
			n = 0
			for i in self.bertie_inputs:
				x = GPIO.input(i)
				print x, " ",
				if x == True:
					GPIO.output(self.pins[n], GPIO.HIGH)
				else:
					GPIO.output(self.pins[n], GPIO.LOW)				
				if n < 2:
					n = n + 1
			print
			time.sleep(1)

	
if __name__ == "__main__":
	'''Called if this file is called standalone. Then just runs a selftest. '''
	logging.basicConfig(filename = LOGFILE,
						filemode='w',
						level=logging.WARNING)	#filemode means that we do not append anymore
#	Default level is warning, level=logging.INFO log lots, level=logging.DEBUG log everything
	logging.warning(datetime.datetime.now().strftime('%d %b %H:%M')+". Running gpio class as a standalone app")
	print 'Cycling outputs - turning on attached leds.'
	myGpio = gpio()
	if TEST_OUTPUT:
		myGpio.sequenceleds()		# use this as a self test
	else:
		myGpio.scan()
	