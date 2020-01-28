#!/usr/bin/python

import RPi.GPIO as GPIO
import time

audPin = 15

GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(audPin, GPIO.OUT)

def do_annoying(freqA = 523, freqB = 622, freqC = 415, duration = 0.25):
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
        do_annoying()
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

def play_song():
    do_beep(627, 0.3)
    time.sleep(0.02)
    do_beep(704, 0.3)
    time.sleep(0.02)
    do_beep(790, 0.3)
    time.sleep(0.02)
    do_beep(704, 0.3)
    time.sleep(0.02)
    do_beep(627, 0.3)

do_annoying_seq()

#play_song()
