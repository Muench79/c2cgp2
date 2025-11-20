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
import threading
import inspect

__version__ = "1.0.0b"

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
    """A class for controlling a car.

        Attributes:
            VERSION (str): Version of the DataStorage class
            __file_ext (tuple): Includes the supported file formats
            storage (bool): Activates data storage
    """
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0) -> None:
        """Initializes the data storage.
        
            Args:
                forward_A (int): 0,1 (Configuration of the rotation direction of a motor). Defaults to 0.
                forward_B (int): 0,1 (Configuration of the rotation direction of the other motor). Defaults to 0.
                turning_offset (int): Offset used to calculate the angle. Defaults to 0.
        """
        __version__ = "1.0.0b"
        log_message("DEBUG", 'Create BaseCar object')
        self._backwheels = BackWheels(forward_A, forward_B)
        self._frontwheels = FrontWheels(turning_offset)
        self._datastorage = DataStorage()
        self._steering_angle = None
        self._direction = None
        self.stop_event = threading.Event()
        self.thread = None

    
    def save_data(self, path, format : str = '' , overwrite : bool = False) -> int:
        """Saves the data to a file and returns detailed information.

            Args:
                path (str): File path
                overwrite (bool): True - Any existing file will be overwritten. False - The filename is appended with a timestamp. Default to False
            
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
    def storage(self) -> bool:
        """Returns the data storage status.

            Returns:
                bool: True - Data is recorded
                      False - Data is not recorded  
        """ 
        return self._datastorage.storage
    
    @storage.setter
    def storage(self, x : bool):
        """Sets the data storage status.

            Args:
                x (bool): True - Data is recorded
                          False - Data is not recorded 
        """
        self._datastorage.storage = x

    @property
    def speed(self) -> int:
        """Returns the current speed.
        """
        return self._backwheels.speed

    @speed.setter
    def speed(self, new_speed : int):
        """Sets the speed to the passed value..

            Args:
                new_speed (int): New value for speed
        """
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
    def steering_angle(self) -> int:
        """Returns the current steering angle.

            Returns:
                int: Current steering angle
        """
        return self._steering_angle
    
    @steering_angle.setter
    def steering_angle(self, new_steering_angle):
        """Sets the steering angle to the passed value.
        """
        self._steering_angle = self._frontwheels.turn(new_steering_angle)
        self._datastorage.add_data('steering_angle', new_steering_angle)
        print(self._steering_angle)

    @property
    def direction(self) -> int:
        """Returns the current direction of travel.

            Returns:
                int: -1 - Direction of travel backwards
                      0 - Vehicle is stationary
                      1 - Direction of travel forward
        """
        if self._backwheels.speed == 0:
            return 0
        else:
            return self._direction    
    
    def drive(self, new_speed : int = None , new_steering_angle : int = None ) -> None:
        """Sets the current speed and steering angle to the specified values.

            Args:
                new_speed (int): New speed value
                new_steering_angle (int): New steering angle
        """
        if not (new_speed is None):
            self.speed = new_speed
        if not (new_steering_angle is None):
            self.steering_angle = new_steering_angle
    
    def stop(self) -> None:
        """Stop the vehicle and straighten the steering wheel.
        """
        self._backwheels.stop()
        self.steering_angle = 90

    def driving_mode_1(self) -> None:
        """Driving mode 1.

            The car first drives forward in a straight line for 3 seconds at a speed of 30.
            Then it stops for a second.
            It then drives backwards straight ahead at a speed of 30 for 3 seconds.
            Then stop the car and driving mode 1 will end.
            The car should now have returned to the point where it started.
        """
        self.drive(30, 90)
        if self.stop_event.wait(3): return
        self.stop()
        if self.stop_event.wait(1): return
        self.drive(-30, 90)
        if self.stop_event.wait(3): return
        self.stop()

    def driving_mode_2(self) -> None:
        """Driving mode 2.

            The car first drives forward in a straight line for 1 second at a speed of 30.
            Then, the steering is turned fully to the right for 8 seconds (at the same speed).
            Then, the vehicle is driven in reverse for 8 seconds at a speed of -30 with the same steering angle.
            Finally, the vehicle reverses for one second with the steering wheel fully turned and then comes to a stop.
            The car should now have returned to the point where it started.
        """
        self.drive(30, 90)
        if self.stop_event.wait(1): return
        self.drive(30, 135)
        if self.stop_event.wait(8): return
        self.drive(-30, 135)
        if self.stop_event.wait(8): return
        self.drive(-30, 90)
        if self.stop_event.wait(1): return
        self.stop()

class SonicCar(BaseCar):
    """A class for controlling a car and an ultrasonic sensor.
    """
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0, preparation_time: float = 0.01, impuls_length: float = 0.00001, timeout: float = 0.05):
        """Initializes the data storage.

            Args:
                Args:
                forward_A (int): 0,1 (Configuration of the rotation direction of a motor). Defaults to 0.
                forward_B (int): 0,1 (Configuration of the rotation direction of the other motor). Defaults to 0.
                turning_offset (int): Offset used to calculate the angle. Defaults to 0.
                preparation_time (float): Waiting time in milliseconds before sending the ultrasound pulse.
                impuls_length (float): Length of the ultrasound pulse.
                timeout (float): waiting time before stopping the measurement in form of the maximum measurement duration.
        """
        super().__init__(forward_A, forward_B, turning_offset)
        self._ultrasonic = Ultrasonic(preparation_time, impuls_length, timeout)

    def get_distance(self) -> int:
        """Returns distance in cm or an error.
            
            Error types:
                -1: Low signal and timeout reached
                -2: High signal and timeout reached
                -3: Negative distance
                -4: Error in time measurement

            Returns:
                int: Distance in cm for a single measurement. Negative values for errors.
        """
        distance = self._ultrasonic.distance()
        self._datastorage.add_data('distance', distance)
        return distance
    
    def get_data(self) -> dict:
        """Returns the stored data.

            Returns:
                dict: all saved data
        """
        return self._datastorage.get_data() 
    
    def clear_data(self):
        """Deletes all previously stored data
        """
        self._datastorage.clear_data()

    def driving_mode_3(self) -> None:
        """Driving mode 3.

            The car is traveling straight ahead at a speed of 30.
            If an obstacle is detected via the ultrasonic sensor, it stops immediately.
        """
        self.drive(30, 90)
        while not self.stop_event.is_set():
            distance = self.get_distance()
            if distance in [-3, -4, -2]:
                pass
            elif distance < 10:
                break
        self.stop()

    def driving_mode_4(self):
        """Driving mode 4.

            The car is on a reconnaissance mission. It drives straight ahead at a speed of 30.
            As soon as an obstacle is detected, the car reverses with maximum steering lock until the obstacle is gone.
            Then it continues its original journey.
            The journey will end automatically after 30 seconds.
        """
        self.drive(30, 90)
        t = time.time()
        while ((time.time() - t) < 30) and not self.stop_event.is_set():
            distance = self.get_distance()
            if distance in [-3, -4, -2]:
                pass
            elif distance < 10 and self.direction == 1:
                self.drive(-30, 135)
            elif distance > 10 and self.direction == -1:
                self.drive(30, 90)
            if self.stop_event.wait(0.1): return
        self.stop()

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
        while ((time.time() - t) < 60) and not self.stop_event.is_set():
            timestamp = time.time()
            infrared_data_analog = self._read_analog(timestamp)
            infrared_data_digital = self._read_digital(timestamp)
            infrared_data_min = min(infrared_data_analog)
            print("p1", infrared_data_analog)
            if infrared_data_min < 40:
                break
            if self.stop_event.wait(0.5): return
        self.drive(30, 90)
        t = time.time()
        while ((time.time() - t)) < 3 and not self.stop_event.is_set():
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
            if self.stop_event.wait(0.1): return
            print(min_value_pos)
            if infrared_data_min < 40:
                t = time.time()
        self.stop()
        self.driving_mode_cancel = False

    def driving_mode_6(self):
        t = time.time()
        while ((time.time() - t) < 60) and not self.stop_event.is_set():
            timestamp = time.time()
            infrared_data_analog = self._read_analog(timestamp)
            infrared_data_digital = self._read_digital(timestamp)
            infrared_data_min = min(infrared_data_analog)
            print("p1", infrared_data_analog)
            if infrared_data_min < 50:
                break
            if self.stop_event.wait(0.5): return
        self.drive(30, 90)
        t = time.time()
        t2 = time.time()
        while ((time.time() - t) < 5) and not self.stop_event.is_set():
            print(t, t2)
            timestamp = time.time()
            infrared_data_analog = self._read_analog(timestamp)
            infrared_data_digital = self._read_digital(timestamp)
            count_threshold = sum(1 for v in infrared_data_analog if v < 50)
            infrared_data_min = min(infrared_data_analog)
            min_value_pos = infrared_data_analog.index(infrared_data_min) if infrared_data_min < 40 and count_threshold == 1 else -1
            print(min_value_pos, infrared_data_min)
            if count_threshold > 0:
                t = time.time()
                t2 = time.time()

            if min_value_pos == 4:
                self.drive(45, 145)
            elif min_value_pos == 3:
                self.drive(45, 112.5)
            elif min_value_pos == 2:
                self.drive(45, 90)
            elif min_value_pos == 1:
                self.drive(45, 67.5)
            elif min_value_pos == 0:
                self.drive(45, 45)
            if self.stop_event.wait(0.1): return
            print(min_value_pos)
            if (time.time() - t2) > 1:
                if self.direction == 1:
                    if self.steering_angle > 90:
                        self.drive(-30, 45)
                    elif self.steering_angle < 90:
                        self.drive(-30, 135)
                    else:
                        self.drive(-30, 90)
 
        pass

    def driving_mode_7(self):
        t = time.time()
        while ((time.time() - t) < 60) and not self.stop_event.is_set():
            timestamp = time.time()
            infrared_data_analog = self._read_analog(timestamp)
            infrared_data_digital = self._read_digital(timestamp)
            infrared_data_min = min(infrared_data_analog)
            print("p1", infrared_data_analog)
            if infrared_data_min < 50:
                break
            if self.stop_event.wait(0.5): return
        self.drive(30, 90)
        t = time.time()
        t2 = time.time()
        t3 = time.time()
        while ((time.time() - t) < 5) and not self.stop_event.is_set():
            print(t, t2)
            timestamp = time.time()
            infrared_data_analog = self._read_analog(timestamp)
            infrared_data_digital = self._read_digital(timestamp)
            count_threshold = sum(1 for v in infrared_data_analog if v < 50)
            infrared_data_min = min(infrared_data_analog)
            min_value_pos = infrared_data_analog.index(infrared_data_min) if infrared_data_min < 40 and count_threshold == 1 else -1
            print(min_value_pos, infrared_data_min)
            if count_threshold > 0:
                t = time.time()
                t2 = time.time()

            if min_value_pos == 4:
                self.drive(45, 145)
            elif min_value_pos == 3:
                self.drive(45, 112.5)
            elif min_value_pos == 2:
                self.drive(45, 90)
            elif min_value_pos == 1:
                self.drive(45, 67.5)
            elif min_value_pos == 0:
                self.drive(45, 45)
            if self.stop_event.wait(0.1): return
            print(min_value_pos)
            if (time.time() - t2) > 1:
                if self.direction == 1:
                    if self.steering_angle > 90:
                        self.drive(-30, 45)
                    elif self.steering_angle < 90:
                        self.drive(-30, 135)
                    else:
                        self.drive(-30, 90)
            if (time.time() - t3) > 0.1:
                print("kkkk")
                t3 = time.time()
                distance = self.get_distance()
                print(distance, "jdkljkdljkldskjlfkdlsökgföldksjm")
                if distance in [-3, -4, -2]:
                    pass
                elif distance < 10 and self.direction == 1:
                    self.drive(0, 0)
                    print("Hindernis erkannt")
                    self.stop()
                    return
            
    
    def _driving_mode_dash(self, mode):
        print("_driving_mode_dash", mode)
        if mode == "driving_mode_1":
            self.driving_mode_1()
        elif mode == "driving_mode_2":
            self.driving_mode_2()
        elif mode == "driving_mode_3":
            self.driving_mode_3()
        elif mode == "driving_mode_4":
            self.driving_mode_4()
        elif mode == "driving_mode_5":
            self.driving_mode_5()
        elif mode == "driving_mode_6":
            self.driving_mode_6()
        elif mode == "driving_mode_7":
            self.driving_mode_7()
        
    def driving_mode_dash(self, mode):
        print("driving_mode_dash", mode)
        #print("läuft noch", self.thread.is_alive())
        if self.thread and self.thread.is_alive():
            print("trhread läugft noch")
            return
        self.thread = threading.Thread(target=self._driving_mode_dash, args=(mode, ))
        self.thread.start()

if __name__ == '__main__':
    def print_all_docstrings(cls):
        print(f"📘 Klasse: {cls.__name__}")
        print(inspect.getdoc(cls) or "  (keine Docstring)\n")

        for name, member in inspect.getmembers(cls):
            if inspect.isfunction(member) or inspect.ismethod(member):
                doc = inspect.getdoc(member)
                print(f"🔹 Methode: {name}")
                print(f"  {doc or '(keine Docstring)'}\n")
            elif not name.startswith("__") and not inspect.isbuiltin(member):
                doc = getattr(cls, name).__doc__
                if doc:
                    print(f"🔸 Attribut: {name}")
                    print(f"  {doc}\n")


    print_all_docstrings(BaseCar)
    sys.exit()
    print("Statrte")
    car = SensorCar(forward_A, forward_B, turning_offset, references=[3,3,3,3,3])
    car._driving_mode_dash("")
    
    car.thread.join()
    

    #while car.thread.isAlive():
    #    pass
    #car.stop()
    #car.storage = True
    #car.driving_mode_1()
    #car.drive(0,90)
    #car.stop()
    #car.save_data('./line_test.csv', overwrite=False)
    print("ggggggggg")
    sys.exit("7777")
    car.fahrmodus_4()
    car.stop()
    #print(car.savedata('./data.csv'))
    sys.exit()
    sleep(3)
        

        #print(car.getdata())
    pprint.pprint(car.getdata())
        #car = CarTest(BaseCar(forward_A, forward_B, turning_offset))
