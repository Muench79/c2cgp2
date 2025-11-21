class BaseCar:
    def __init__(self):
        print("Hallo, ich wurde gerade gebaut!")
        self._speed = 0
        self._gang = 1
 
    # Getter und Setter für Speed
    @property
    def speed(self):
        print("Der aktuelle Speed ist:")
        return self._speed
 
    @speed.setter
    def speed(self, new_speed):
        print(f"Der alte Speed ist {self._speed}, der neue ist {new_speed}")
        self._speed = new_speed
 
    # Getter und Setter für Gang
    @property
    def gang(self):
        return self._gang
 
    @gang.setter
    def gang(self, neuer_gang):
        if self._speed > 5 and neuer_gang < 0:
            print("So nicht – Rückwärtsgang bei zu hoher Geschwindigkeit!")
        else:
            print(f"Der Gang wird auf {neuer_gang} gesetzt.")
            self._gang = neuer_gang
 
    # Drive-Methode
    def drive(self, speed):
        print(f"Das Auto fährt jetzt mit {speed} km/h.")
        self._speed = speed
 
 
# Test
car = BaseCar()
print(car.speed)
 
car.gang = 2
car.drive(6)
car.gang = -1
 
