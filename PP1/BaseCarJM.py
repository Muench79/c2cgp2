from basisklassen import BackWheels, FrontWheels, Ultrasonic, Infrared
from DataStorage import DataStorage
from time import sleep
import time
import json
import os
import sys
import pprint
import logging
import time

# Logger erstellen
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

# Handler für Konsole
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Format definieren
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Handler hinzufügen
logger.addHandler(console_handler)

def log_message(level, message, **kwargs):
    # Format and generate log message
    param_str = " | ".join(f"{key}={value}" for key, value in kwargs.items())
    full_message = f"{message} | {param_str}" if param_str else message


    if level == "DEBUG":
        logger.debug(full_message)
    elif level == "INFO":
        logger.info(full_message)
    elif level == "WARNING":
        logger.warning(full_message)
    elif level == "ERROR":
        logger.error(full_message)
    elif level == "CRITICAL":
        logger.critical(full_message)
    else:
        logger.info(f"Unbekannter Loglevel '{level}': {full_message}")


try:
    with open("config.json", "r") as f:
        data = json.load(f)
        turning_offset = data["turning_offset"]
        forward_A = data["forward_A"]
        forward_B = data["forward_B"]
    log_message('DEBUG', 'Read config.json: ' , data = data)
    print("Daten in config.json:")
    print(" - Turning Offset: ", turning_offset)
    print(" - Forward A: ", forward_A)
    print(" - Forward B: ", forward_B)
except Exception as e:
    log_message('INFO', 'Read failed config.json : ' , error = e)
    print("Keine geeignete Datei config.json gefunden!")
    turning_offset = 0
    forward_A = 0
    forward_B = 0

class BaseCar():
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0) -> None:
        log_message("DEBUG", 'Create BaseCar object')
        self._backwheels = BackWheels(forward_A, forward_B)
        self._frontwheels = FrontWheels(turning_offset)
        self._datastorage = DataStorage()
        self._steering_angle = None
        self._direction = None
    
    def save_data(self, path, format : str = '' , overwrite : bool = False) -> int:
        """Saves the data to a file and returns detailed information

            Args:
                path (str): File path
                overwrite (bool): 

            Returns:
                int: 0 (Storage successful)
                    -1 (The filename was not specified)
                    -2 (The directory does not exist)
                    -3 (The file format is not supported)
                    -4 (The file already exists)
                    -5 (An error occurred while writing the file)
                    -6 (Unknown error (please contact support))
        """
        return self._datastorage.save_data(path, format, overwrite)
    
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
        self._datastorage.add_data('speed', new_speed)
        self._backwheels.speed = abs(new_speed)

    @property
    def steering_angle(self):
        return self._steering_angle
    
    @steering_angle.setter
    def steering_angle(self, new_steering_angle):
        self._steering_angle = self._frontwheels.turn(new_steering_angle)
        self._datastorage.add_data('steering_angle', new_steering_angle)
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
        self.steering_angle = 90

    def driving_mode_1(self):
        self.drive(30, 90)
        time.sleep(3)
        self.stop()
        time.sleep(1)
        self.drive(-30, 90)
        time.sleep(3)
        self.stop()

    def driving_mode_1(self):
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
        distance = self._ultrasonic.distance()
        self._datastorage.add_data('distance', distance)
        return distance
    
    def get_data(self):
        return self._datastorage.get_data() 
    
    def clear_data(self):
        self._datastorage.clear_data()

    def driving_mode_3(self):
        self.drive(30, 90)
        while True:
            distance = self.get_distance()
            print(distance)
            if distance in [-3, -4, -2]:
                pass
            elif distance < 10:
                break
        self.stop()
    
    def driving_mode_4(self):
        self.drive(30, 90)
        t = time.time()
        while True and (time.time() - t) < 30:
            distance = self.get_distance()
            print(distance)
            if distance in [-3, -4, -2]:
                pass
            elif distance < 10 and self.direction == 1:
                self.drive(-30, 135)
            elif distance > 10 and self.direction == -1:
                self.drive(30, 90)
            time.sleep(0.1)

class SensorCar(SonicCar):
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0, preparation_time: float = 0.01, impuls_length: float = 0.00001, timeout: float = 0.05, references: list = [300, 300, 300, 300, 300]):
        super().__init__(forward_A, forward_B, turning_offset, preparation_time, impuls_length, timeout)
        self._infrared = Infrared(references)
        print(self._infrared.read_analog())
    
    def _read_analog(self, timestamp = None):
        infrared_data_analog = self._infrared.read_analog()
        for i, v in enumerate(infrared_data_analog):
            self._datastorage.add_data(f'infrared_analog_{i}', infrared_data_analog[i], timestamp)
        return infrared_data_analog
    
    def _read_digital(self, timestamp = None):
        infrared_data_digital = self._infrared.read_digital()
        for i, v in enumerate(infrared_data_digital):
            self._datastorage.add_data(f'infrared_data_digital{i}', infrared_data_digital[i], timestamp)
        return infrared_data_digital
    
    def driving_mode_5(self):
        t = time.time()
        while (time.time() - t) < 60:
            timestamp = time.time()
            infrared_data_analog = self._read_analog(timestamp)
            infrared_data_digital = self._read_digital(timestamp)
            infrared_data_min = min(infrared_data_analog)
            print("p1", infrared_data_analog)
            if infrared_data_min < 40:
                break
            time.sleep(0.5)
        self.drive(30, 90)
        t = time.time()
        while (time.time() - t) < 3:
            timestamp = time.time()
            infrared_data_analog = self._read_analog(timestamp)
            infrared_data_digital = self._read_digital(timestamp)
            count_threshold = sum(1 for v in infrared_data_analog if v < 40)
            infrared_data_min = min(infrared_data_analog)
            min_value_pos = infrared_data_analog.index(infrared_data_min) if infrared_data_min < 40 and count_threshold == 1 else -1
            print(min_value_pos, infrared_data_min)
            if min_value_pos == 4:
                self.drive(30, 145)
            elif min_value_pos == 3:
                self.drive(30, 112.5)
            elif min_value_pos == 2:
                self.drive(30, 90)
            elif min_value_pos == 1:
                self.drive(30, 67.5)
            elif min_value_pos == 0:
                self.drive(30, 45)
            time.sleep(0.1)
            print(min_value_pos)
            if infrared_data_min < 40:
                t = time.time()
        self.stop()
    def driving_mode_6(self):
        pass
    def driving_mode_7(self):
        pass
if __name__ == '__main__':
    print("Statrte")
    car = SensorCar(forward_A, forward_B, turning_offset, references=[3,3,3,3,3])
    car.stop()
    car.storage = True
    car.driving_mode_5()
    car.drive(0,90)
    #car.stop()
    car.save_data('./line_test.csv', overwrite=False)
    sys.exit()
    car.fahrmodus_4()
    car.stop()
    #print(car.savedata('./data.csv'))
    sys.exit()
    sleep(3)
    

    #print(car.getdata())
    pprint.pprint(car.getdata())
    #car = CarTest(BaseCar(forward_A, forward_B, turning_offset))