#!/usr/bin/env python  
## adapted from https://github.com/adeept/Adeept_Ultimate_Starter_Kit_Python_Code_for_RPi

import RPi.GPIO as GPIO  
import time
from datetime import time as CLOCK


BIT0 = 3   
BIT1 = 5  
BIT2 = 24  
BIT3 = 26  

segCode = [0x3f,0x06,0x5b,0x4f,0x66,0x6d,0x7d,0x07,0x7f,0x6f]  #0~9  
pins = [11,12,13,15,16,18,22,7,3,5,24,26]  
bits = [BIT0, BIT1, BIT2, BIT3]
ALARM_PIN = 32
BUTTON_PIN = 36
CHANGE_PIN = 38

## alarm variable, set to 00:00:00 by default
alarm_time = CLOCK(23, 50)
alarm_on = False

## time variable, set to 23:32:00 by default
clock_time = CLOCK(23, 40)

def print_msg():  
	print 'Program is running...'  
	print 'Please press Ctrl+C to end the program...'  

def digitalWriteByte(val):  
	GPIO.output(11, val & (0x01 << 0))  
	GPIO.output(12, val & (0x01 << 1))  
	GPIO.output(13, val & (0x01 << 2))  
	GPIO.output(15, val & (0x01 << 3))  
	GPIO.output(16, val & (0x01 << 4))  
	GPIO.output(18, val & (0x01 << 5))  
	GPIO.output(22, val & (0x01 << 6))  
	GPIO.output(7,  val & (0x01 << 7))  

## if we had a real-time clock, we would get the time here.
## for now It'll just increment the clock time
def change_clock_time():

        global clock_time

        minutes = clock_time.minute
        hours = clock_time.hour

        if minutes == 59:
                minutes = 0
                hours = hours + 1
                if hours == 24:
                        hours = 0
        else:
                minutes = minutes + 1

        clock_time = CLOCK(hours, minutes)

def change_alarm_time():

        global alarm_time

        minutes = alarm_time.minute
        hours = alarm_time.hour

        ## counts how many time units have passed since the last button press
        ## so the alarm can be set, car-clock-style
        delay_counter = 0

        while delay_counter < 5:
                if GPIO.input(CHANGE_PIN) == False: ## active low
                        if minutes == 59:
                                minutes = 0
                                hours = hours + 1
                                if hours == 24:
                                        hours = 0
                        else:
                                minutes = minutes + 1
                        delay_counter = 0
                        
                alarm_time = CLOCK(hours, minutes)
                for i in range(50):
                        display(alarm_time)
                ## add a little flash to show we are setting the time
                time.sleep(0.15)
                delay_counter = delay_counter + 1

        ## reset delay counter and sleep for a bit to show change to hour set
        delay_counter = 0
        time.sleep(2)

        while delay_counter < 5:
                if GPIO.input(CHANGE_PIN) == False: ## active low
                        if hours == 23:
                                hours = 0
                        else:
                                hours = hours + 1
                        delay_counter = 0

                alarm_time = CLOCK(hours, minutes)
                for i in range(50):
                        display(alarm_time)
                ## add a little flash to show we are setting the time
                time.sleep(0.15)
                delay_counter = delay_counter + 1

        return
                


## handles displaying the time on the 7-segment
## each run of this method is ~8 milliseconds
def display(clock):
	b0 = clock.minute % 10  
	b1 = clock.minute % 100 / 10   
	b2 = clock.hour % 10 
	b3 = clock.hour % 100 / 10
	
        GPIO.output(BIT0, GPIO.LOW)  
        digitalWriteByte(segCode[b0])  
        time.sleep(0.002)  
        GPIO.output(BIT0, GPIO.HIGH)   
        GPIO.output(BIT1, GPIO.LOW)
        digitalWriteByte(segCode[b1])  
        time.sleep(0.002)  
        GPIO.output(BIT1, GPIO.HIGH)  
        GPIO.output(BIT2, GPIO.LOW)  
        digitalWriteByte(segCode[b2])  
        time.sleep(0.002)  
        GPIO.output(BIT2, GPIO.HIGH)   
        GPIO.output(BIT3, GPIO.LOW)  
        digitalWriteByte(segCode[b3])  
        time.sleep(0.002)  
        GPIO.output(BIT3, GPIO.HIGH)

## checks if the alarm is on and turns it on if so
def check_alarm_on():
        global alarm_on

        ## check if alarm needs to be triggered
        if alarm_time.hour == clock_time.hour and alarm_time.minute == clock_time.minute:
                alarm_on = True

        ## trigger alarm if applicable
        if alarm_on == True:
                GPIO.output(ALARM_PIN, GPIO.HIGH)
        else:
                GPIO.output(ALARM_PIN, GPIO.LOW)

## checks if the alarm button is pressed, to turn off the alarm
def check_turn_alarm_off():
        global alarm_on
        if GPIO.input(BUTTON_PIN) == False: ## active low
                alarm_on = False
                
def setup():        
	GPIO.setmode(GPIO.BOARD)    #Number GPIOs by its physical location  
	GPIO.setwarnings(False)
	for pin in pins:  
		GPIO.setup(pin, GPIO.OUT)    #set all pins' mode is output  
		GPIO.output(pin, GPIO.HIGH)  #set all pins are high level(3.3V)

	## setup the alarm pin
	GPIO.setup(ALARM_PIN, GPIO.OUT)
	GPIO.output(ALARM_PIN, GPIO.LOW)

	## setup the push buttons
	GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(CHANGE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


## loop that keeps the clock running
def loop():
        print_msg()

	while True:  
		change_clock_time()
		check_alarm_on()
		check_turn_alarm_off()
		
                if GPIO.input(CHANGE_PIN) == False: ## active low
                        change_alarm_time()
                        
		for i in range(100):  
			display(clock_time)

def destroy():   #When program ending, the function is executed.   
	for pin in pins:    
		GPIO.output(pin, GPIO.LOW) #set all pins are low level(0V)   
		GPIO.setup(pin, GPIO.IN)   #set all pins' mode is input
	GPIO.output(ALARM_PIN, GPIO.LOW)


if __name__ == '__main__': #Program starting from here   
	setup()   
	try:  
		loop()    
	except KeyboardInterrupt:    
		destroy()    
