from basisklassen import BackWheels, FrontWheels, Ultrasonic
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

"""
class BaseCar():
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0):
        self._backwheels = BackWheels(forward_A, forward_B, turning_offset)
        self._frontwheels = FrontWheels(turning_offset)

    @property
    def speed(self):
        self._backwheels.
"""




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
    
    def drive(self, new_speed : int = None , new_steering_angle : int = None ):
        if not (new_speed is None):
            self.speed = new_speed
        if not (new_steering_angle is None):
            self.steering_angle = new_steering_angle
    
    def stop(self):
        self._speed = 0
        self.left_wheel.speed = 0
        self.right_wheel.speed = 0
        self.steering_angle = 90

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

class SonicCar(BaseCar, Ultrasonic):
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0, preparation_time: float = 0.01, impuls_length: float = 0.00001, timeout: float = 0.05):
        BaseCar.__init__(self, forward_A, forward_B, turning_offset)
        Ultrasonic.__init__(self, preparation_time, impuls_length, timeout)
    
    def get_distance(self):
        return self.distance()
    
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
            if distance < 0:
                break
            elif distance < 10:
                break
            time.sleep(1)
        self.stop()



if __name__ == '__main__':
    
    car = SonicCar(forward_A, forward_B, turning_offset)
    car.stop()
    car.fahrmodus_3()
    

    #car = CarTest(BaseCar(forward_A, forward_B, turning_offset))