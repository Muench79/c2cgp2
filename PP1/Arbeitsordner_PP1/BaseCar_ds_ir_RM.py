
#from DataStorage import DataStorage
import click
import time
import numpy as np
import pandas as pd 
import math
import RPi.GPIO as GPIO
import smbus
import json
import os
import sys
import csv


from Abschluss_PP1.basisklassen import BackWheels, FrontWheels,PWM, Ultrasonic, Infrared
# Liest nur die ausgewählten Basisklassen ein
# Die basisklassen.py wird nicht editiert!!
# Notwendigen Klassen werden importiert und mit einem Hinweis versehen. 

'''
Import von Klassen aus der basisklassen.py
    > Nutzung der Classen front 
    > Zeile 226  
    >class FrontWheels(object) 
    > Lenkwinkel
    > Backwheels Zeile 309
    > class BackWheels(object): 
    > Steuert die Motoren an
'''
'''
Einlesen config.sys
   > Initiale Einlesung der config.jason für übergabe der Startwerte Lenkwinkel ggf. Drehrichtung Raeder
'''


try:
# Beginn einlesen config.json für Setzung Startwerte und Offsets
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


class data_storage():
# Klasse data_storage zur Speicherung und Protokollierung der Fahrdaten in einer Log-File
    def __init__(self): 
    # self wichtig um aus der Klasse ein Objekt machen mit eigener Speicherung in ein Dictionary welches einzelne Liste der Parameter enthält
        self.data_storage = {"timestamp":[],"speed":[], "steering_angle": [], "direction":[], "ultrasonic":[], "Infrared":[]}
     
    def drive_parkour_1(self):
    # def drive_parkour Test der Funktionen zum schreiben des Datenspeichers
        for i in range(20):
            self.data_storage["timestamp"].append(i)
            self.data_storage["speed"].append(i)
            self.data_storage["steering_angle"].append(i)
            self.data_storage["direction"].append(i)
            self.data_storage["ultrasonic"].append(i)
            self.data_storage["Infrared"].append(i)
#        df = pd.Dataframe(self.data_storage)
    def add_data (self, speed, steering_angle, direction, ultrasonic, Infrared):
    # add_Data fügt Daten in die jeweilgen Listen zur Speicherung des Log-Files 
        self.data_storage["timestamp"].append(time.time())
        self.data_storage["speed"].append(speed)
        self.data_storage["steering_angle"].append(steering_angle)
        self.data_storage["direction"].append(direction)
        self.data_storage["ultrasonic"].append(ultrasonic)
        self.data_storage["Infrared"].append(Infrared) 
    def save_log(self):
    # Schreib die gespeicherten Daten aus dem Dict (mit Inhalt Listen in die Datei data_storage.csv)
        df = pd.DataFrame.from_dict(self.data_storage)
        df.to_csv("data_storage.csv", index=False)



# Klasse BaseCar wird erstellt und ziehen uns die Werte forward_A,B turning_offset 
# damit erstellen wir zwei Objekt self._backwheels und self._frontwheels und 
# verbknüpfen diese mit den Parametern forward_A,B und turning_offset
#class cali_ref (Infrared):
#    def cali_test(self):
#        Infrared.cali_references(self)
#        return Infrared.cali_references
class BaseCar():
    '''
    Klasse BaseCar wird erstellt und übernimmt die Werte forward_A,B turning_offset 
    Anschließend werden die Objekte self._backwheels und self._frontwheels erstellt und 
    verbknüpfen diese mit den Parametern forward_A,B und turning_offset
    '''
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0):
        self._backwheels = BackWheels(forward_A, forward_B)
        self._frontwheels = FrontWheels(turning_offset)
        self._data_storage = data_storage()
        self._steering_angle = None # Selbstdefiniere Variable in der der Lenkwinkel gespeichert wird - Anfangsbedingung None weil kein Winkel bekannt
        self._direction = None # Selbstdefiniere Variable in der der Richtung gespeichert wird - Anfangsbedingung None weil kein Richtung bekannt
        print("OK")
    

    @property
    def speed(self):
        #holt sich die aktuelle Geschw. von der Kl. backwheels und gibt diese zurück
        return self._backwheels.speed 
    @speed.setter
    def speed(self, new_speed : int):
        # Setzt die Geschwindigkeit und ermittelt die Fahrtrichtung
        if new_speed < 0:
            self._backwheels.backward()
            self._direction = -1 #Wenn die geschw. negativ ist dann wird self._direction auf -1 gesetzt für spätere Richtungserkennung sinnvoll
        else: 
            self._backwheels.forward()
            self._direction = 1
        if new_speed > 100:
            new_speed = 100
        elif new_speed < -100:
            new_speed = -100
        #self._backwheels.speed muss immer gesetzt sein (gleiche Zeilenposition wie elif bzw. IF)
        self._backwheels.speed = abs(new_speed) #negative Werte der Geschwindigkeit werden pos. gespeichert - Vorbereitung Datastorage
        #

    @property
    def steering_angle(self):
        #Ausgabe aktueller Lenkwinkel Variable ist selbst gewählt und in Zeile 103 BasisClasse initialisiert (self)
        return self._steering_angle 
    
    @steering_angle.setter
    def steering_angle(self, new_steering_angle):
        # Setzen des neuen Lenkwinkels 
        self._steering_angle = self._frontwheels.turn(new_steering_angle)
        print(self._steering_angle)

    @property
    def direction(self):
        #Richtungsrückgabe wenn Geschw.=0 ist die Richtung 0 = stehen, direction = 1 Vowärtsfahrt, direction = -1 Rückwärts
        if self._backwheels.speed == 0: #Richtungsrückgabe wenn Geschw. =0 ist die Richtung 0 = stehen
            return 0
        else:
            return self._direction  #Definition in Speed-Setter  
    
    def drive(self, new_speed : int = None , new_steering_angle : int = None ):
        # Vorgabe der Geschwindigkeit und Lenkwinkel für späteren Funktionsaufruf in den Fahrmodi 
        if not (new_speed is None):
            self.speed = new_speed
        if not (new_steering_angle is None):
            self.steering_angle = new_steering_angle
    
    def stop(self):
        # Stoppfunktion setzt V=0 und Lenkwinkel auf 90°
        self._backwheels.stop()
        self.steering_angle = 90

class SonicCar(BaseCar):
    #Initialisierung Sonicar bezogen auf die Eltern-Klasse Basecar
    #Implemntierung von <ultraschallsensoren aus der Ultrasonic Klasse aus basisklassen.py
    def __init__(self,forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0, preparation_time: float = 0.01, impuls_length: float = 0.00001, timeout: float = 0.05):
       super().__init__(forward_A, forward_B, turning_offset)
       self.ultrasonic = Ultrasonic(preparation_time, impuls_length, timeout) #Verbindung zu Ultrasonic aus Basisklassen
#       
       
       
    def car_distance(self): 
        #Distanz wird aus Berechnung der basisklasse Ultrasonis.py Zeile 45ff gebildet. 
        for i in range(5):
            distance = self.ultrasonic.distance()  
            if distance < 0:
                unit = 'Error'
            else:
                unit = 'cm'
            print('{} : {} {}'.format(i, distance, unit))
            time.sleep(.5)   
    def tc_dist(self): 
        #Methode zur Abstandsmeesung ohn Einheit wird erzeugt
        return self.ultrasonic.distance()
    
class SensorCar(SonicCar):
    '''
    Erzeugung der Klasse SensorCar auf Basis Elternklasse SonicCar 
    Über super()._init__ werden die Parameter 
    forward_A, forward_B, turning_offset, preparation_time, impuls_length, timeout initialisiert
    Weiterhin wird die Methode rferences aus der basisklassen.py aus der Klasse Infrared überneommen
    '''
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0, preparation_time: float = 0.01, impuls_length: float = 0.00001, timeout: float = 0.05, references: list = [300, 300, 300, 300, 300]):
        super().__init__(forward_A, forward_B, turning_offset, preparation_time, impuls_length, timeout)
        self.infra_ref = Infrared(references) 
        self.min_right_angle = self._frontwheels._straight_angle + 20 #initalisierung minimaler Lenkwinkel für Ausweichmanöver
        self.min_left_angle = self._frontwheels._straight_angle - 20 #initalisierung minimaler Lenkwinkel für Ausweichmanöver
        self._break_analog_value = None # Erzeugung einer Variablen für IR Abbruchbedingung "aktuell keine Verwedung"
        self._max_analog_value = None #Erzeugt einer Variablen für IR Abbruch soll dem max Wert im Array oder Liste finden
        self._min_analog_value = None # #Erzeugt einer Variablen für IR Abbruch soll dem max Wert im Array oder Liste findenbreak Bedingung
        
    def array(self):
        # Gibt die IR Informationen als Liste / Array zurück
        print('{} : {}'.format(self.infra_ref.read_analog()))
        return self.infra_ref.read_analog()
    
    def cali_test(self):
        #Calibrierunstest aus der bassisklassen.py Dient zur Voreinstellung der IR Werte am Potentiometer CAR
        #Werte solltn ca. bei 50 liegen [50, 50, 50, 50, 50] für Fmod 7 und Fmod 8 siehe Fmod Beschreibung
        self.infra_ref.cali_references()

    def digital(self) -> list:
        # List die IR Werte und gibt diese digital zurück 0 od. 1
        """Reads the value of the infrared module as digital.

        Returns:
            [list]: List of digitized measurement of the sensors using the reference as threshold.
        """

        new_analog = np.array(self.infra_ref.read_analog())
        new_digital = np.where(new_analog < self.infra_ref._references, 0, 1)

        min_analog_value = min(new_analog)
        #min_analog_value
        min_analog_index = list(new_analog).index(min_analog_value) 
        #print(new_digital[0])
        #print(min_analog_index)
        return list(new_digital)  #Return übergibt ausgabe Wert der Methode. Dieser kann dann durch den aufruf x.digial usw abgefragt werden
    
    
    def analog(self) -> list:
        #Liefert die aktuellen IR - Werte und speichert ermittelt den Min, Max Wert sowie den Index(Position) des Min-Wet im Array
        #_break_analaog_value für eine noch zu definierende Funktion aktuell nicht verwendet
        new_analog = np.array(self.infra_ref.read_analog())
        self._min_analog_value = min(new_analog)
        min_analog_index = list(new_analog).index(self._min_analog_value) 
        #self._break_analog_value = self._min_analog_value * 2
        self._max_analog_value = max(new_analog)
        #print(f"{new_analog} new_analog meth_analog")
        #print(f"{min_analog_index} min_analog_Index")
        #print(f"{self._min_analog_value} min analog_value")
        #print(f"break_analog_value {self._break_analog_value}")
        #print(f"max_analog_value {self._max_analog_value}")
        return min_analog_index
    
    

        
#x = SonicCar(forward_A, forward_B, turning_offset)
x = SensorCar(forward_A, forward_B, turning_offset)
x.car_distance()
# Erstellung eines Objekts vom Typ SensorCar und damit auch zugriff auf die Parameter der Klasse mit x.
#x.car_distance()
#Aufruf der Mehode car_distance() wird nur zu Testzwecken genutzt kann bei bedarf aktiviert werden
s=data_storage()
#Erstellung eines Objekts vom Typ Datenstorage dient zur Speicherung von Messdaten
#self.data_storage = {"timestamp":[],"speed":[], "steering_angle": [], "direction":[], "ultrasonic":[], "Infrared":[]}
#df = pd.Dataframe(data_storage)
#s.drive_parkour_1() # Methode wird aufgerufen
#s.save_log() # Methode wird aufgerufen

def run_mode(fmod: int, x: SensorCar): 
# Methode zur Auswahl der Fahrmodi über die Dashboard.py 
    start_zeit = time.time()
    zeitgrenze = 80  #ausführbare Funktion definieren, um im Dashboard aufzurufen 
    """ Es wäre auch möglich def run_mode(fmod, x): zu schreiben. Int und SensorCar sind nur Hinweise für den Programmierer dass fmod eine ganzzahl sein muss und x ein 
        Objekt der Kalsse SensorCar sein muss    """
    if fmod == 1:
        '''
        Das Auto fährt mit langsamer Geschwindigkeit
        etwa 3 Sekunden geradeaus, stoppt für etwa 1 Sekunde und fährt dann etwa
        3 Sekunden rückwärts.
        '''
        print('Fahrmodus 1 wird ausgeführt')
        x.drive(25, x._frontwheels._straight_angle)
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        time.sleep(3)
        x.drive(-25, x._frontwheels._straight_angle)  # uebergibt nur die Geschwindigkeit
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        time.sleep(3)
        x.stop()
        x._data_storage.save_log()
        

    if fmod == 2:
        '''
        Das Auto fährt 1 Sekunde geradeaus, dann für 8 Sekunden mit maximalen Lenkwinkel im Uhrzeigersinn und
        stoppt. Dann soll das Auto diesen Fahrplan in umgekehrter Weise abfahren und an
        den Ausgangspunkt zurückkehren. Die Vorgehensweise soll für eine Fahrt im entgegengesetzten
        Uhrzeigersinn wiederholt werden.
        '''
        print('Fahrmodus 2 wird ausgeführt')
        # fahrmodus rechts
        x.drive(20, x._frontwheels._straight_angle) #
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        time.sleep(1)
        x.drive(20, x._frontwheels._max_angle )  #[self._max_angle]???
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        time.sleep(8)
        x.stop()
        x.drive(-20, x._frontwheels._max_angle)
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        time.sleep(8)
        x.drive(-20, x._frontwheels._straight_angle)
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        time.sleep(1)
        x.stop()
        # fahrmodus links
        x.drive(20, x._frontwheels._straight_angle) #
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        time.sleep(1)
        x.drive(20, x._frontwheels._min_angle)  #[self._max_angle]???
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        time.sleep(8)
        x.stop()
        x.drive(-20, x._frontwheels._min_angle)
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        time.sleep(8)
        x.drive(-20, x._frontwheels._straight_angle)
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        time.sleep(1)
        x.stop()
        x._data_storage.save_log()

    if fmod == 3:
        '''
        Fahren bis ein Hindernis im Weg ist und dann stoppen.
        '''
        print('Fahrmodus 3 wird ausgeführt')
        x.drive(45, x._frontwheels._straight_angle)
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        wd=3 #Variable Anzahl der Unterschreitung der Bedingung distance < 10cm für break 
        w=wd #zusätzliche Variable damit spätere Anzahl nur an einer Stelle geändert werden muss
        while True: 
            d=x.tc_dist() #einlesen der distanz aus der Methode
            print(d)
            if d in [-3,-4,-2]: # ignoriert Fehlerfall -3, -2, -4
                pass #ignoriert bzw. mach nichts IF brauch die Anweisung pass
            elif d < 10: 
                w=w-1
                if w == 0: #Abbruch wenn w=0 bedeutet das 3mal der wert kleiner der Vorgabe d=10 erfolgt sind 
                    break
            elif d >= 10: #Wenn >10 dann wird der "counter" neu auf ausgangswert wd in diesem bsp. 3 gesetzt
                w=wd
        print("Ende", d)
        x.stop()
        x._data_storage.save_log()

    if fmod == 4:
        '''
        Fahrzeug variert die Geschwindigkeit in Abhängigkeit der Distanz und fährt bei Hinderniserkennung zurück mit max Lenkwinkel
        '''
        start_zeit = time.time()
        print('Fahrmodus 4 wird ausgeführt')
        x.drive(45, x._frontwheels._straight_angle)
        #s.add(x.speed, x.steering_angle, x.direction, x.ultrasonic)
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        wd=3 #Variable Anzahl der Unterschreitung der Bedingung distance < 10cm für break 
        w=wd #zusätzliche Variable damit spätere Anzahl nur an einer Stelle geändert werden muss
        while True: 
            # Möglichkeit Schleife zu beenden
            d=x.tc_dist() #einlesen der distanz aus der Methode
            print(d)
            if d in [-3,-4,-2]: # ignoriert Fehlerfall -3, -2, -4
                pass #ignoriert bzw. mach nichts IF brauch die Anweisung pass
            elif d >= 15: #Wenn >10 dann wird der "counter" neu auf ausgangswert wd in diesem bsp. 3 gesetzt
                x.drive(45, x._frontwheels._straight_angle)
                w=wd     
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog()) 
            elif d in range(8, 15):
    #           w=wd
                x.drive(20, x._frontwheels._straight_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif d < 8: 
                w=w-1
                if w == 0: #Abbruch wenn w=0 bedeutet das 3mal der wert kleiner der Vorgabe d=10 erfolgt sind 
                    x.stop()
                    while x.tc_dist() < 10:
                        time.sleep(2)
                        x.drive(-25, x._frontwheels._max_angle) #max_angle = 135 Grad rechts
                        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                    x.stop()
                    time.sleep(2)
                    x.drive(45, x._frontwheels._straight_angle)
                    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                    print("Ende", d)
            if time.time() - start_zeit >=zeitgrenze:
                x.stop()
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                print("Exit")
                break
        x._data_storage.save_log()  


    if fmod == 5:
        '''
        Linieverfolgung über Erkennung einer Linie mit großen Kurvenradien
        Lösung über Auswertung Digitaler Signale der IR Sensoren (Fehleranfällig)
        '''
        x.drive(0, 100)
        #print(x.digital())
        x.cali_test()
        #print(x.digital())
        time.sleep(3)
        print('Fahrmodus 5 wird ausgeführt')
        #print(x.infra_ref.read_digital())
        #print(x.digital())
        #print(x.digital()[0])
        x.drive(30, x._frontwheels._straight_angle)
        #s.add(x.speed, x.steering_angle, x.direction, x.ultrasonic)
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        wd=3 #Variable Anzahl der Unterschreitung der Bedingung distance < 10cm für break 
        w=wd #zusätzliche Variable damit spätere Anzahl nur an einer Stelle geändert werden muss
        while True: 
            # Möglichkeit Schleife zu beenden
            d=x.tc_dist() #einlesen der distanz aus der Methode
            print(d)
            #print(x.digital())
            if d in [-3,-4,-2]: # ignoriert Fehlerfall -3, -2, -4
                print(x.digital())
    #            print(x.new_analog())
                pass #ignoriert bzw. mach nichts IF brauch die Anweisung pass
            elif d < 5: 
                w=w-1
                if w == 0: #Abbruch wenn w=0 bedeutet das 3mal der wert kleiner der Vorgabe d=10 erfolgt sind 
                    time.sleep(2)
                    #print(x.infra_ref.read_digital())
                    #print(x.digital())
                    #print(x.digital()[0])
                    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog()) 
                    x.stop()
                    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog()) 

            elif x.digital()[2] == 0:
                x.drive(30, x._frontwheels._straight_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            
            elif x.digital()[0] & x.digital()[1] == 0:
                x.drive(30, x.min_left_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                
            
            elif x.digital()[0]  == 0:
                x.drive(30, x._frontwheels._min_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif x.digital()[3] & x.digital()[4] == 0:
                x.drive(30, x.min_right_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif x.digital()[4]  == 0:
                x.drive(30, x._frontwheels._max_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif x.digital()== [0, 0, 0, 0, 0]:
                x.stop()
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog()) 
                print("Linienverfolgung beendet")   
            if time.time() - start_zeit >=zeitgrenze:
                x.stop()
                print("Exit")
                break
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        x._data_storage.save_log()  

    if fmod == 6:
        '''Linieverfolgung über Erkennung einer Linie mit großen Kurvenradien
           Lösung über Auswertung Analoge Signale der IR Sensoren 
        '''
        x.drive(0, 100)
        #print(x.digital())
        x.cali_test()
        #print(x.digital())
        time.sleep(3)
        print('Fahrmodus 6 wird ausgeführt')
        
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        ir_ref = 25
        while True: 
            # Möglichkeit Schleife zu beenden
            #d=x.tc_dist() #einlesen der distanz aus der Methode
            _index = x.analog()
            print(f"indexwhile {_index}")

            count_threshold = sum(1 for v in x.infra_ref.read_analog() if v < ir_ref) #Ermittlung Anzahl von Werte unterhal der Schwelle
            print(f"count {count_threshold}")
            print(f" red analog {x.infra_ref.read_analog()}")
            if x._min_analog_value >= ir_ref or count_threshold == 0:
                _index = -1
                x.stop()
                print("Linienverfolgung beendet")
                break
            
            if _index == 2: 
                x.drive(30, x._frontwheels._straight_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif _index == 1:
                x.drive(30, x.min_left_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())    
            elif _index == 0:
                x.drive(30, x._frontwheels._min_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif _index == 3:
                x.drive(30, x.min_right_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif _index  == 4:
                x.drive(30, x._frontwheels._max_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            
            if time.time() - start_zeit >=zeitgrenze:
                x.stop()
                print("Time-Exit")
                break
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        x._data_storage.save_log()  

    if fmod == 7:
        '''
        Linieverfolgung über Erkennung einer Linie mit sehr engen Kurvenradien inkl. Korrekturfahrten Rückwärts
        Lösung über Auswertung Analoger Signale der IR Sensoren 
        Ermittlung eines Referenzwertes für die Verlassenserkennung der Linie 
        IR Sensoren über den basisklassen IR Test Nummer 4 auf Werte um ca. 50 einstellen [50, 50, 50, 50, 50]
        Einstellung über Potentiometer an der Sesorbar vom Auto (blauer Kasten)
        '''
        x.drive(0, 100)
        #print(x.digital())
        #x.cali_test()
        #print(x.digital())
        time.sleep(3)
        print('Fahrmodus 7 wird ausgeführt')
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        while True: 
            # Möglichkeit Schleife zu beenden
            #d=x.tc_dist() #einlesen der distanz aus der Methode
            ir_ref = (np.mean(x.infra_ref.read_analog())) * 0.85
            print(f"ir_ref {ir_ref}")
            _index = x.analog()
            print(f"indexwhile {_index}")
            count_threshold = sum(1 for v in x.infra_ref.read_analog() if v < ir_ref) #Ermittlung Anzahl von Werte unterhal der Schwelle
            print(f"count {count_threshold}")
            print(f" red analog {x.infra_ref.read_analog()}")
            if x._min_analog_value >= ir_ref or count_threshold == 0:
                _index = -1
                if x.direction == 1:
                        if x.steering_angle > 90:
                            x.drive(0, 45)
                            time.sleep(0.1)
                            x.drive(-30, 45)
                            time.sleep(0.3)
                            x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                        elif x.steering_angle < 90:
                            x.drive(0, 135)
                            time.sleep(0.1)
                            x.drive(-30, 135)
                            time.sleep(0.3)
                            x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                        else:
                            x.drive(-30, 90)
                            time.sleep(0.4)
                            x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                # 
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                #time.sleep(0.5)
                print("Linie verloren rückwärts")
                #time.sleep(1.5)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                        
                continue
                #print("Linienverfolgung beendet")
                #break
            
            if _index == 2: 
                x.drive(30, x._frontwheels._straight_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif _index == 1:
                x.drive(30, x.min_left_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())    
            elif _index == 0:
                x.drive(20, x._frontwheels._min_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif _index == 3:
                x.drive(30, x.min_right_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif _index  == 4:
                x.drive(20, x._frontwheels._max_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            
            if time.time() - start_zeit >=zeitgrenze:
                x.stop()
                print("Time-Exit")
                #print(f"max a {max_ir}")
                #print(f" break_a {break_ir}")
                break
            
        ["Index"].append(_index) 
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        x._data_storage.save_log()  

    if fmod == 8:
        '''
        Linieverfolgung über Erkennung einer Linie mit sehr engen Kurvenradien inkl. Korrekturfahrten Rückwärts
        Lösung über Auswertung Analoger Signale der IR Sensoren 
        Ermittlung eines Referenzwertes für die Verlassenserkennung der Linie 
        IR Sensoren über den basisklassen IR Test Nummer 4 auf Werte um ca. 50 einstellen [50, 50, 50, 50, 50]
        Einstellung über Potentiometer an der Sesorbar vom Auto (blauer Kasten)
        Zusätzlich sind die Ultraschallsensoren eingebunden damit vor einem Hindernis gestoppt wird
        '''
        x.drive(0, 100)
        wd=3 #Variable Anzahl der Unterschreitung der Bedingung distance < 10cm für break 
        w=wd #zusätzliche Variable damit spätere Anzahl nur an einer Stelle geändert werden muss
        #x.cali_test()
        time.sleep(3)
        print('Fahrmodus 7 wird ausgeführt')
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        while True: 
            #Möglichkeit Schleife zu beenden
            d=x.tc_dist() #einlesen der distanz aus der Methode
            print(f" Abstand {d}")
            print(f" Fehlerschleife {w}")
            #ir_ref = (x._max_analog_value + x._min_analog_value) / 2
            ir_ref = (np.mean(x.infra_ref.read_analog())) * 0.85
            #print(f"ir_ref {ir_ref}")
            _index = x.analog()
            #print(f"indexwhile {_index}")
            count_threshold = sum(1 for v in x.infra_ref.read_analog() if v < ir_ref) #Ermittlung Anzahl von Werte unterhal der Schwelle
            #print(f"count {count_threshold}")
            #print(f" red analog {x.infra_ref.read_analog()}")
            if d in [-3,-4,-2]: # ignoriert Fehlerfall -3, -2, -4
                pass #ignoriert bzw. mach nichts IF brauch die Anweisung pass
            elif d >= 10: #Wenn >10 dann wird der "counter" neu auf ausgangswert wd in diesem bsp. 3 gesetzt
                w=wd     
                pass
            elif d < 8: 
                w=w-1
                if w <= 0: #Abbruch wenn w=0 bedeutet das 3mal der wert kleiner der Vorgabe d=10 erfolgt sind 
                    x.stop()
                    time.sleep(5.0)
            if x._min_analog_value >= ir_ref or count_threshold == 0:
                _index = -1
                if x.direction == 1:
                        if x.steering_angle > 90:
                            x.drive(0, 45)
                            time.sleep(0.1)
                            x.drive(-30, 45)
                            time.sleep(0.3)
                            x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                        elif x.steering_angle < 90:
                            x.drive(0, 135)
                            time.sleep(0.1)
                            x.drive(-30, 135)
                            time.sleep(0.3)
                            x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                        else:
                            x.drive(-30, 90)
                            time.sleep(0.4)
                            x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                # 
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                #time.sleep(0.5)
                print("Linie verloren rückwärts")
                #time.sleep(1.5)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
                        
                continue
                #print("Linienverfolgung beendet")
                #break
            
            if _index == 2: 
                x.drive(30, x._frontwheels._straight_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif _index == 1:
                x.drive(30, x.min_left_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())    
            elif _index == 0:
                x.drive(20, x._frontwheels._min_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif _index == 3:
                x.drive(30, x.min_right_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            elif _index  == 4:
                x.drive(20, x._frontwheels._max_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
            
            if time.time() - start_zeit >=zeitgrenze:
                x.stop()
                print("Time-Exit")
                break
           
        ["Index"].append(_index) 
        x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
        x._data_storage.save_log()  

    if fmod == 9:
        # Bricht das Progrmm ab
        print('Abbruch')
        sys.exit()

    #while True:
    #    try:
    #        fmod = int(input("Für Abbruch Bitte die 9: "))
    #        break
    #    except ValueError:
    #        print("Bitte eine gültige Ganzzahl eingeben.")
   


if __name__ == "__main__":                                                             
    # Konsolenausführung in if-Schleife kapseln, damit sie nicht vom Dash-Board aufgerufen werden kann
    #nur wenn das Skript direkt gestartet wird vergibt Python dem Modul den Namen __name__ == "__main__"
    #wird das Skript jedoch geladen setzt python __name__ == "BaseCar_ds_ir"  --> Konsolenausführung wird nicht aufgerufen
    

    print('-- Waehle eine Fahrmodus aus--')
    print('1: = Fmod1: Vfw=low 3sec > stopp 1s > Vbw=low 3sec')
    print('2: = Fmod2: Vfw=low 1sec > 8sec max arg right > stopp > 8sec Vbw max arg right > Vbw=low 1sec > repeat to left')
    print('3: = Fmod3: Vfw=low and stopp wenn distance <10cm stopp Vorwärtsfahrt bis Hindernis:')
    print('4: = Fmod4: Vfw = variabel bei Hinterniss max Lenkwinkel und zurück Erkundungstour')
    print('5: = Fmod5: Vfw = IR -Fahrmodus digital muss überarbeitet werden')
    print('6: = Fmod6: Vfw = IR Fahrmodus analog inkl. Stoppfunktion')
    print('7: = Fmod7: Vfw = IR Fahrmdus wie Fmod6 mit erweiterter Linierverfolgung')
    print('8: = Fmod8: Vfw = IR Fahrmdus wie Fmod7 mit Stoppfunktion')
    print('9: = Abbruch')

    
    while True:
    # Aufruf zur Auswahl der Fahrmodi ohne Dasboard direkt aus der .py Datei
        try:
            fmod = int(input("Bitte Fahrmodus eingeben: "))
            break
        except ValueError:
            print("Bitte eine gültige Ganzzahl eingeben.")

    run_mode(fmod, x)
    

