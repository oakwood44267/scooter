#!/usr/bin/python

import RPi.GPIO as GPIO
import time

audPin = 10

GPIO.setmode(GPIO.BOARD) # Broadcom pin-numbering scheme
GPIO.setup(audPin, GPIO.OUT)

def do_chord(freqA = 523, freqB = 622, freqC = 415, duration = 0.25):
    # Notes: C5 D#5 G#4.  Taken from a train horn chord. 
    incrementA = 1.0 / 2.0 / freqA
    incrementB = 1.0 / 2.0 / freqB
    incrementC = 1.0 / 2.0 / freqC

    next = time.time() + incrementA
    end = time.time() + duration

    while time.time() < end:
        GPIO.output(audPin, GPIO.LOW)
        while time.time() < next:
            pass

        next = time.time() + incrementA

        GPIO.output(audPin, GPIO.HIGH)
 
        while time.time() < next:
            pass

        next = time.time() + incrementA

        GPIO.output(audPin, GPIO.LOW)
        while time.time() < next:
            pass

        next = time.time() + incrementB

        GPIO.output(audPin, GPIO.HIGH)
 
        while time.time() < next:
            pass

        next = time.time() + incrementB

        GPIO.output(audPin, GPIO.LOW)
        while time.time() < next:
            pass

        next = time.time() + incrementC

        GPIO.output(audPin, GPIO.HIGH)
 
        while time.time() < next:
            pass

        next = time.time() + incrementC

def do_annoying_seq():
    for i in range(5):
        do_chord()
        time.sleep(0.1)

def do_beep(freq = 625, duration = 0.3):
    increment = 1.0 / 2.0 / freq

    next = time.time() + increment
    end = time.time() + duration

    while time.time() < end:
        GPIO.output(audPin, GPIO.LOW)
        while time.time() < next:
            pass

        next = time.time() + increment

        GPIO.output(audPin, GPIO.HIGH)
 
        while time.time() < next:
            pass

        next = time.time() + increment 

def play_shark():
    do_beep(523, 0.5)
    time.sleep(0.02)
    do_beep(587, 0.5)
    time.sleep(0.02)
    do_beep(698, 0.25)
    time.sleep(0.02)
    do_beep(698, 0.25)
    time.sleep(0.02)
    do_beep(698, 0.25)
    time.sleep(0.02)
    do_beep(698, 0.125)
    time.sleep(0.02)
    do_beep(698, 0.25)
    time.sleep(0.02)
    do_beep(698, 0.125)
    time.sleep(0.02)
    do_beep(698, 0.25)
    time.sleep(0.02)
    do_beep(698, 0.25)
    time.sleep(0.02)
    do_beep(698, 0.25)
    time.sleep(0.02)
    do_beep(659, 0.25)
    time.sleep(0.02)

def play_fourth():
    do_beep(523, 0.13)
    do_beep(698, 0.13)
    do_beep(784, 0.35)
#    do_beep(830, 0.20)

if __name__ == "__main__": 
    play_fourth()
