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
#
start_zeit = time.time()
zeitgrenze = 80 

#datastorage_list = []
##data2 = []
#datastorageDict = {}
from basisklassen import BackWheels, FrontWheels,PWM, Ultrasonic, Infrared
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

# Klasse BaseCar wird erstellt und ziehen uns die Werte forward_A,B turning_offset 
# damit erstellen wir zwei Objekt self._backwheels und self._frontwheels und 
# verbknüpfen diese mit den Parametern forward_A,B und turning_offset
#class cali_ref (Infrared):
#    def cali_test(self):
#        Infrared.cali_references(self)
#        return Infrared.cali_references
class data_storage():
    def __init__(self): # self wichtig um aus der Klasse ein Objekt machen mit eigener speicherung 
        self.data_storage = {"timestamp":[],"speed":[], "steering_angle": [], "direction":[], "ultrasonic":[], "Infrared":[]}
     
    def drive_parkour_1(self):#Test der Funktionen
        for i in range(20):
            self.data_storage["timestamp"].append(i)
            self.data_storage["speed"].append(i)
            self.data_storage["steering_angle"].append(i)
            self.data_storage["direction"].append(i)
            self.data_storage["ultrasonic"].append(i)
            self.data_storage["Infrared"].append(i)
#        df = pd.Dataframe(self.data_storage)
    def add_data (self, speed, steering_angle, direction, ultrasonic, Infrared):
        self.data_storage["timestamp"].append(time.time())
        self.data_storage["speed"].append(speed)
        self.data_storage["steering_angle"].append(steering_angle)
        self.data_storage["direction"].append(direction)
        self.data_storage["ultrasonic"].append(ultrasonic)
        self.data_storage["Infrared"].append(Infrared) 
    def save_log(self):
        df = pd.DataFrame.from_dict(self.data_storage)
        df.to_csv("data_storage.csv", index=False)

#,columns= self.data_storage.keys()


class BaseCar():
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0):
        self._backwheels = BackWheels(forward_A, forward_B)
        self._frontwheels = FrontWheels(turning_offset)
        self._data_storage = data_storage()
        self._steering_angle = None # Selbstdefiniere Variable in der der Lenkwinkel gespeichert wird - Anfangbedingung None weil kein Winkel bekannt
        self._direction = None # Selbstdefiniere Variable in der der Richtung gespeichert wird - Anfangbedingung None weil kein Richtung bekannt
        print("OK")
    

    @property
    def speed(self):
        return self._backwheels.speed #holt sich die aktuelle Geschw. von der Kl. backwheels und gibt diese zurück

    @speed.setter
    def speed(self, new_speed : int):
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
            #self._datastorage.adddata('speed', new_speed)
        self._backwheels.speed = abs(new_speed) #negative Werte der geschwindigkeit werden pos. gespeichert - Vorbereitung Datastorage

    @property
    def steering_angle(self):
        return self._steering_angle #Ausgabe aktueller Lenkwinkel Variable ist selbt gewählt siehe Zeile 53
    
    @steering_angle.setter
    def steering_angle(self, new_steering_angle):
        self._steering_angle = self._frontwheels.turn(new_steering_angle)
        print(self._steering_angle)

    @property
    def direction(self):
        if self._backwheels.speed == 0: #Richtungsrückgabe wenn Geschw. =0 ist die Richtung 0 = stehen
            return 0
        else:
            return self._direction  #Definition in Speed-Setter  
    
    def drive(self, new_speed : int = None , new_steering_angle : int = None ):
        if not (new_speed is None):
            self.speed = new_speed
        if not (new_steering_angle is None):
            self.steering_angle = new_steering_angle
    
    def stop(self):
        self._backwheels.stop()
        self.steering_angle = 90

class SonicCar(BaseCar):
    def __init__(self,forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0, preparation_time: float = 0.01, impuls_length: float = 0.00001, timeout: float = 0.05):
       super().__init__(forward_A, forward_B, turning_offset)
       self.ultrasonic = Ultrasonic(preparation_time, impuls_length, timeout) #Verbindung zu Ultrasonic aus Basisklassen
#       
       
       
    def car_distance(self): 
        for i in range(5):
            distance = self.ultrasonic.distance() #Distanz wird aus Berechnung der Basisklasse Ultrasonis Zeile 45ff gebildet. 
            if distance < 0:
                unit = 'Error'
            else:
                unit = 'cm'
            print('{} : {} {}'.format(i, distance, unit))
            time.sleep(.5)   
    def tc_dist(self):
        return self.ultrasonic.distance()
    
class SensorCar(SonicCar):
    def __init__(self, forward_A: int = 0, forward_B: int = 0, turning_offset: int = 0, preparation_time: float = 0.01, impuls_length: float = 0.00001, timeout: float = 0.05, references: list = [300, 300, 300, 300, 300]):
        super().__init__(forward_A, forward_B, turning_offset, preparation_time, impuls_length, timeout)
        self.infra_ref = Infrared(references)
        self.min_right_angle = self._frontwheels._straight_angle + 20
        self.min_left_angle = self._frontwheels._straight_angle - 20
        self._break_analog_value = None
        self._max_analog_value = None
        self._min_analog_value = None # break Bedingung
        
    def array(self):
        print('{} : {}'.format(self.infra_ref.read_analog()))
        return self.infra_ref.read_analog()
    
    def cali_test(self):
        self.infra_ref.cali_references()

    def digital(self) -> list:
        """Reads the value of the infrared module as digital.

        Returns:
            [list]: List of digitized measurement of the sensors using the reference as threshold.
        """

        new_analog = np.array(self.infra_ref.read_analog())
        new_digital = np.where(new_analog < self.infra_ref._references, 0, 1)

        min_analog_value = min(new_analog)
        #min_analog_value
        min_analog_index = list(new_analog).index(min_analog_value) 
        print(new_digital[0])
        print(min_analog_index)
        return list(new_digital)  #Return übergibt ausgabe Wert der MEthode. Dieser kann dann durch den aufruf x.digial usw abgefragt werden
    
    
    def analog(self) -> list:
        new_analog = np.array(self.infra_ref.read_analog())
        self._min_analog_value = min(new_analog)
        min_analog_index = list(new_analog).index(self._min_analog_value) 
        self._break_analog_value = self._min_analog_value * 2
        self._max_analog_value = max(new_analog)
        print(f"{new_analog} new_analog meth_analog")
        print(f"{min_analog_index} min_analog_Index")
        print(f"{self._min_analog_value} min analog_value")
        print(f"break_analog_value {self._break_analog_value}")
        print(f"max_analog_value {self._max_analog_value}")
        return min_analog_index
    
    

'''
    def infra(self):
        
        return self.infra_ref.read_analog()
        print('{} : {}'.format(self.infra_ref))
'''   
        

#timestamp,speed,steering_angle,direction,distance
# Datenaufzeichnung und Speicherung   
#x = SonicCar(forward_A, forward_B, turning_offset)
x = SensorCar(forward_A, forward_B, turning_offset)
#_array, _index = x.digital()
#print(f" test_analog_W1_W {_array, _index}")
#print(f"Index = {_index}")
x.car_distance()
s=data_storage()
#c=cali_ref()
#data_storage = {"timestamp":[],"speed":[], "direction": [], "steering_angle":[], "ultrasonic":[]}

#df = pd.Dataframe(data_storage)

#s.drive_parkour_1() # Methode wird aufgerufen
#s.save_log() # Methode wird aufgerufen

#sys.exit()

 #           for row in csvDaten:
 #               datum, startort, zielort, kilometer_start, kilometer_ende, zweck, privatfahrt = row
 #               fzg.addJourneyEintrag(datum, startort, zielort, kilometer_start, kilometer_ende, zweck, privatfahrt)
 # Objekt muss für die Classe Datastorage erschaffen werden
#s.add()
#print(s)
        
        
'''    
        with open(f"fahrdaten_1.csv", "w", encoding="utf-8") as file:
        file.write() 
        # Kopfzeile schreiben
        writer.writerow(header)
'''
   
#x = BaseCar(forward_A, forward_B, turning_offset) #Ist die Intanz der Klasse BaseCar

print('-- Waehle eine Fahrmodus aus--')
print('1: = Fmod1: Vfw=low 3sec > stopp 1s > Vbw=low 3sec')
print('2: = Fmod2: Vfw=low 1sec > 8sec max arg right > stopp > 8sec Vbw max arg right > Vbw=low 1sec > repeat to left')
print('3: = Fmod3: Vfw=low and stopp wenn distance <10cm stopp Vorwärtsfahrt bis Hindernis:')
print('4: = Fmod4: Vfw = variabel bei Hinterniss max Lenkwinkel und zurück Erkundungstour')
print('5: = Fmod5: Vfw = IR -Fahrmodus digital muss überarbeitet werden')
print('6: = Fmod6: Vfw = IR Fahrmodus analog inkl. Stoppfunktion')
print('7: = Fmod7: Vfw = IR Fahrmdus wie Fmod6 mit erweiterter Linierverfolgung')
print('8: = Abbruch')
while True:
    try:
        fmod = int(input("Bitte Fahrmodus eingeben: "))
        break
    except ValueError:
        print("Bitte eine gültige Ganzzahl eingeben.")
                          
if fmod == 1:
    print('Fahrmodus 1 wird ausgeführt')
    x.drive(25, x._frontwheels._straight_angle)
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
    time.sleep(3)
    x.drive(-25, x._frontwheels._straight_angle)  # uebergibt nur die Geschwindigkeit
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
    time.sleep(3)
    x.stop()
    x._data_storage.save_log()
    

if fmod == 2:
    print('Fahrmodus 2 wird ausgeführt')
    # fahrmodus rechts
    x.drive(20, x._frontwheels._straight_angle) #
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
    time.sleep(1)
    x.drive(20, x._frontwheels._max_angle )  #[self._max_angle]???
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
    time.sleep(8)
    x.stop()
    x.drive(-20, x._frontwheels._max_angle)
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
    time.sleep(8)
    x.drive(-20, x._frontwheels._straight_angle)
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
    time.sleep(1)
    x.stop()
    # fahrmodus links
    x.drive(20, x._frontwheels._straight_angle) #
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
    time.sleep(1)
    x.drive(20, x._frontwheels._min_angle)  #[self._max_angle]???
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
    time.sleep(8)
    x.stop()
    x.drive(-20, x._frontwheels._min_angle)
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
    time.sleep(8)
    x.drive(-20, x._frontwheels._straight_angle)
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
    time.sleep(1)
    x.stop()
    x._data_storage.save_log()

if fmod == 3:
    print('Fahrmodus 3 wird ausgeführt')
    x.drive(45, x._frontwheels._straight_angle)
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
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
    start_zeit = time.time()
    print('Fahrmodus 4 wird ausgeführt')
    x.drive(45, x._frontwheels._straight_angle)
    #s.add(x.speed, x.steering_angle, x.direction, x.ultrasonic)
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
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
            x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())   
        elif d in range(8, 15):
 #           w=wd
            x.drive(20, x._frontwheels._straight_angle)
            x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
        elif d < 8: 
            w=w-1
            if w == 0: #Abbruch wenn w=0 bedeutet das 3mal der wert kleiner der Vorgabe d=10 erfolgt sind 
                x.stop()
                while x.tc_dist() < 10:
                   time.sleep(2)
                   x.drive(-25, x._frontwheels._max_angle) #max_angle = 135 Grad rechts
                   x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
                x.stop()
                time.sleep(2)
                x.drive(45, x._frontwheels._straight_angle)
                x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
                print("Ende", d)
        if time.time() - start_zeit >=zeitgrenze:
            x.stop()
            x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist())
            print("Exit")
            break
    x._data_storage.save_log()  


if fmod == 5:
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
        max_ir = x._max_analog_value
        break_ir = x._break_analog_value
        _index = x.analog()
        #print(f"max a x_ {x._break_analog_value}")
        #print(f" break_a_x. {x._max_analog_value}")
        #print(f"max a {max_ir}")
        #print(f" break_a {break_ir}")
        #print(d)
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
            print(f"max a {max_ir}")
            print(f" break_a {break_ir}")
            break
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
    x._data_storage.save_log()  

if fmod == 7:
    x.drive(0, 100)
    #print(x.digital())
    x.cali_test()
    #print(x.digital())
    time.sleep(3)
    print('Fahrmodus 7 wird ausgeführt')
    x._data_storage.add_data(x.speed, x.steering_angle, x.direction, x.tc_dist(), x.analog())
    #ir_ref = 10 Wieder einkommentieren wenn threshold nicht Funktionsfähig

    while True: 
        # Möglichkeit Schleife zu beenden
        #d=x.tc_dist() #einlesen der distanz aus der Methode
        #ir_ref = (x._max_analog_value + x._min_analog_value) / 2
        ir_ref = (np.mean(x.infra_ref.read_analog())) * 0.85
        print(f"ir_ref {ir_ref}")
        #max_ir = x._max_analog_value
        #break_ir = x._break_analog_value
        _index = x.analog()
        #print(f"max a x_ {x._break_analog_value}")
        #print(f" break_a_x. {x._max_analog_value}")
        #print(f"max a {max_ir}")
        #print(f" break_a {break_ir}")
        #print(d)
        print(f"indexwhile {_index}")
        #Index = []
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
    print('Abbruch')
    sys.exit()

while True:
    try:
        fmod = int(input("Für Abbruch Bitte die 7: "))
        break
    except ValueError:
        print("Bitte eine gültige Ganzzahl eingeben.")
   



    




   #   x._max_angle
#print(turning_offset)
#print(x._max_angle)
