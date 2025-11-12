from basisklassen import BackWheels, FrontWheels, Ultrasonic, Infrared
from DataStorage import DataStorage
from time import sleep
import time
import json
import os
import sys
import pprint

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

class BaseCar():
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0):
        self._backwheels = BackWheels(forward_A, forward_B)
        self._frontwheels = FrontWheels(turning_offset)
        self._datastorage = DataStorage()
        self._steering_angle = None
        self._direction = None
        print("OK")
    @property
    def storage(self):
        return self._datastorage.storage
    
    @storage.setter
    def storage(self, x : bool):
        self._datastorage.storage = x

    @property
    def speed(self):
        return self._backwheels.speed

    @speed.setter
    def speed(self, new_speed : int):
        if new_speed < 0:
            self._backwheels.backward()
            self._direction = -1
        elif new_speed >= 0:
            self._backwheels.forward()
            self._direction = 1
        if new_speed > 100:
            new_speed = 100
        elif new_speed < -100:
            new_speed = -100
        self._datastorage.adddata('speed', new_speed)
        self._backwheels.speed = abs(new_speed)

    @property
    def steering_angle(self):
        return self._steering_angle
    
    @steering_angle.setter
    def steering_angle(self, new_steering_angle):
        self._steering_angle = self._frontwheels.turn(new_steering_angle)
        self._datastorage.adddata('steering_angle', new_steering_angle)
        print(self._steering_angle)

    @property
    def direction(self):
        if self._backwheels.speed == 0:
            return 0
        else:
            return self._direction    
    
    def drive(self, new_speed : int = None , new_steering_angle : int = None ):
        if not (new_speed is None):
            self.speed = new_speed
        if not (new_steering_angle is None):
            self.steering_angle = new_steering_angle
    
    def stop(self):
        self._backwheels.stop()
        #self.steering_angle = 90

    def fahrmodus_1(self):
        self.drive(30, 90)
        time.sleep(3)
        self.stop()
        time.sleep(1)
        self.drive(-30, 90)
        time.sleep(3)
        self.stop()

    def fahrmodus_2(self):
        self.drive(30, 90)
        time.sleep(1)
        self.drive(30, 135)
        time.sleep(8)
        self.drive(-30, 135)
        time.sleep(8)
        self.drive(-30, 90)
        time.sleep(1)
        self.stop()

class SonicCar(BaseCar):
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0, preparation_time: float = 0.01, impuls_length: float = 0.00001, timeout: float = 0.05):
        super().__init__(forward_A, forward_B, turning_offset)
        self._ultrasonic = Ultrasonic(preparation_time, impuls_length, timeout)

    def get_distance(self):
        self._datastorage.adddata('distance', self._ultrasonic.distance())
        return self._ultrasonic.distance()
    
    def getdata(self):
        return self._datastorage.getdata() 
    
    def cleardata(self):
        self._datastorage.cleardata()

    def fahrmodus_3(self):
        self.drive(30, 90)
        while True:
            distance = self.get_distance()
            print(distance)
            if distance in [-3, -4, -2]:
                pass
            elif distance < 10:
                break
        self.stop()
    
    def fahrmodus_4(self):
        self.drive(30, 90)
        while True:
            distance = self.get_distance()
            print(distance)
            if distance < 0 and self.direction == 1:
                self.drive(-30, 135)
            elif distance < 10 and self.direction == -1:
                self.drive(30, 90)
            elif distance < 10:
                break
            time.sleep(1)
        self._basecar.stop()

class SensorCar(SonicCar):
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0, preparation_time: float = 0.01, impuls_length: float = 0.00001, timeout: float = 0.05, references: list = [300, 300, 300, 300, 300]):
        super().__init__(forward_A, forward_B, turning_offset, preparation_time, impuls_length, timeout)
        self._infrared = Infrared(references)
        print(self._infrared.read_analog())
    
if __name__ == '__main__':
    
    car = SensorCar(forward_A, forward_B, turning_offset)
    car.storage = True
    car.stop()
    #car.fahrmodus_4()

    sleep(3)
    car.stop()
    print(car.getdata())
    pprint.pprint(car.getdata())
    #car = CarTest(BaseCar(forward_A, forward_B, turning_offset))

