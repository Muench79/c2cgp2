from Abschluss_PP1.basisklassen import BackWheels, FrontWheels
import time
import json
import os
import sys

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


class BaseCar(BackWheels, FrontWheels):
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0):
        BackWheels.__init__(self, forward_A, forward_B)
        FrontWheels.__init__(self, turning_offset)
        self._steering_angle = 0
        self._direction = 0
    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self, new_speed : int):
        if new_speed < 0:
            self.right_wheel.backward()
            self.left_wheel.backward()
            self._direction = -1
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

    @property
    def direction(self):
        if self._speed == 0:
            return 0
        else:
            return self._direction    
    def drive(self, new_speed = None, new_steering_angle = None):
        if not (new_speed is None):
            self.speed = new_speed
        if not (new_steering_angle is None):
            self.steering_angle = new_steering_angle
    def stop(self):
        self._speed = 0
        self.left_wheel.speed = 0
        self.right_wheel.speed = 0

x = BaseCar(forward_A, forward_B, turning_offset)
#sys.exit()
x.drive(100, 45)
time.sleep(1)
x.drive(-100, 134)
time.sleep(1)
x.stop()
sys.exit()
x.steering_angle = 45
#x.speed = 100
time.sleep(1)
#x.speed = -100
x.steering_angle = 140
time.sleep(1)
x.speed = 0

