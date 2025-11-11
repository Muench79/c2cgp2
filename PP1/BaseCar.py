import click
import time
import numpy as np
import math
import RPi.GPIO as GPIO
import smbus
import json
import os
import sys
#

from basisklassen import BackWheels, FrontWheels
# Liest nur die ausgewählten Basisklassen ein
#Die basisklassen.py wird nicht editiert
#Notwendigen Klassen werden importiert und mit einem Hinweis versehen. 

'''
Nutzung der Classen front 
Zeile 226  
class FrontWheels(object) 
Lenkwinkel
Backwheels Zeile 309
class BackWheels(object): 
Steuert die Motoren an

Initiale Einlesung der config.jason für übergabe der Startwerte Lenkwinkel ggf. Drehrichtung Raeder
'''
try:
    with open("config.json", "r") as f:
        data = json.load(f)
        turning_offset = data["turning_offset"]
        forward_A = data["forward_A"]
        forward_B = data["forward_B"]
        print("Daten in config.json:")
        print(" - Turning Offset: ", turning_offset)
        print(" - Forward A: ", forward_A)
        print(" - Forward B: ", forward_B)
except:
    print("Keine geeignete Datei config.json gefunden!")
    turning_offset = 0
    forward_A = 0
    forward_B = 0


class BaseCar(BackWheels, FrontWheels): #Klasse initiert mit config.jsaon
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0):
        BackWheels.__init__(self, forward_A, forward_B)
        FrontWheels.__init__(self, turning_offset)
        self._steering_angle = 0
        self._direction = 0
    @property
    def speed(self):  # Setzen und uebergeben der Geschwindigkeit
        return self._speed
    
    @speed.setter   # uebergabe der neuen Parameter für Geschwidigkeit aus der Methode drive()
    def speed(self, new_speed : int):
        if new_speed < 0: # Wenn der Wert kleiner 0 dann Rückwärt 
            self.right_wheel.backward()
            self.left_wheel.backward()
            self._direction = -1 # Variable wird erzeugt wenn Geschw. negative
        elif new_speed >= 0:
            self.left_wheel.forward()
            self.right_wheel.forward()
            self._direction = 1
        new_speed = abs(new_speed)
        if new_speed > 100:
            new_speed = 100
        self._speed = new_speed
        self.left_wheel.speed = new_speed
        self.right_wheel.speed = new_speed

    @property
    def steering_angle(self):
        return self._steering_angle
    
    @steering_angle.setter
    def steering_angle(self, new_steering_angle):
        print(new_steering_angle)

        self._steering_angle = self.turn(new_steering_angle)
        print(self._steering_angle)

    '''
     Umsetzung der Aufgabe 3.1.3 
    direction: Rückgabe der aktuelle Fahrrichtung (1: vorwärts, 0: Stillstand, ‑1 Rückwärts)
    (Property ohne Setter)
    '''
    @property           
    def direction(self):
        if self._speed == 0:
            return 0
        else:
            return self._direction    
    def drive(self, new_speed = None, new_steering_angle = None): #Die Bedienung ist Wahr wenn für den Parmeter ein Wert übergeben wurde (der Wert ist None)
        if not (new_speed is None):   #Wenn kein Wert übergeben wird findet keine Veraenderung statt
            self.speed = new_speed
        if not (new_steering_angle is None):
            self.steering_angle = new_steering_angle
    def stop(self):
        self._speed = 0
        self.left_wheel.speed = 0
        self.right_wheel.speed = 0
        self.steering_angle = 90

#x = BaseCar(forward_A, forward_B, turning_offset)
'''
#sys.exit()
x.drive(0, 45)
time.sleep(1)
x.drive(0, 145)
time.sleep(1)
x.stop()
sys.exit()
x.steering_angle = 45
x.speed = 100
time.sleep(1)
x.speed = -100
x.steering_angle = 140
time.sleep(1)
x.speed = 0
'''

@click.command()
@click.option('--modus', '--m', type=int, default=None, help="Startet Test für Klasse direkt.")
def main(modus):
    print('-- Waehle eine Fahrmodus aus--')
    modi = {
        1: 'Fmod1: Vfw=low 3sec > stopp 1s > Vbw=low 3sec',
        2: 'Fmod2: Vfw=low 1sec > 8sec max arg right > stopp > 8sec Vbw max arg right > Vbw=low 1sec > repeat to left',
    }

'''
if modus == 5:
        try:
            print(os.getcwd())
            with open("config.json", "r") as f:
                data = json.load(f)
                turning_offset = data["turning_offset"]
                forward_A = data["forward_A"]
                forward_B = data["forward_B"]
                print("Daten in config.json:")
                print(" - Turning Offset: ", turning_offset)
                print(" - Forward A: ", forward_A)
                print(" - Forward B: ", forward_B)
        except:
            print("Keine geeignete Datei config.json gefunden!")
        else:
            print("Test der Vorderräder:")
            x = input(' Drücken Sie ENTER zum Start.')
            fw = FrontWheels(turning_offset=turning_offset)
            fw.test()
            time.sleep(1)
            print("Test der Hinterräder:")
            x = input(' ACHTUNG! Das Auto wird ein Stück fahren!\n Drücken Sie ENTER zum Start.')
            bw = BackWheels(forward_A=forward_A, forward_B=forward_B)
            bw.test()
'''
'''''
class Fmod1():
    def __init__(self) -> None:
        pass

class Fmod2():
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0):
        BackWheels.__init__(self, forward_A, forward_B)
        FrontWheels.__init__(self, turning_offset)
        self._steering_angle = 0
        self._direction = 0
'''