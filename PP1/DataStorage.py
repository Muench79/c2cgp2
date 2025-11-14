import time
import json
import os
import sys
import pprint
import re

class DataStorage():

    __fileext = ('.csv', '.json')

    def __init__(self, storage : bool = False):
        self._data = {}
        self._dataprepared = []
        self._storage = storage

    def adddata(self, key, value):
        if self._storage:
            if key not in self._data:
                self._data[key] = [(time.time(), value)]
            else:
                self._data[key].append((time.time(), value))
    
    def getdata(self):
        return self._data

    def getkeys(self):
        return tuple(self._data.keys())
    
    def cleardata(self):
        self._data = {}
        self._dataprepared = []
    
    def _datapreparation(self):
        self._dataprepared = []
        for k, v in self._data.items():
            for t in v:
                self._dataprepared.append({"data_key" : k, "data_time" : t[0], "data_measurement_value" : t[1]})
        if len(self._dataprepared) > 1:
            self._dataprepared.sort(key = lambda x: x['data_time'])

    def _datatocsv(self):
        self._datapreparation()
        datakeys = self.getkeys()
        linehead = [f"{i}" for i in datakeys]
        linehead = 'time,' + ','.join(linehead)
        linescsv = ''
 
        for data in self._dataprepared:
            if linescsv:
                linescsv += '\n'
            linescsv += f"{data['data_time']}"
            for i, dk in enumerate(datakeys):
                if dk in data['data_key']:
                    linescsv += f",{data['data_measurement_value']}"
                else:
                    linescsv += ',NaN'
        if not datakeys:
            return ""
        else:
            return linehead + '\n' + linescsv
 
    def _savedatajson(self, path):
        self._datapreparation()
        try:
            with open(path, 'w', encoding = 'utf-8') as jf:
                json.dump(self._dataprepared, jf, ensure_ascii=False, indent=2)
        except:
            return -1
        return 0
    
    def _savedatacsv(self, path):
        try:
            with open(path, 'w', encoding = 'utf-8') as csvf:
                csvf.write(self._datatocsv())
        except:
            return -1
        return 0

    def savedata(self, path, format : str = '' , overwrite : bool = False):
        folder = os.path.dirname(path)
        filename = os.path.basename(path)
        name, ext = os.path.splitext(filename)
        ext2 = ''

        if not os.path.isdir(folder):
            return -1 # Verzeichnis ist nicht vorhanden
        elif not format: 
            # es ist kein Dateiformat vorgegeben
            if ext == '':
                # ?-File -> .csv
                ext2 = self.__fileext[0]
            elif ext.lower() == self.__fileext[0]:
                # csv-File -> .csv
                ext2 = self.__fileext[0]
            elif ext.lower() == self.__fileext[1]:
                # json-File -> .json
                ext2 = self.__fileext[1]
            else:
                return -2 # Das Dateiformat wird nicht unterstützt
        else:
            # Dateiformat ist vorgegeben
            if format.lower() == self.__fileext[0]:
                # csv-File -> .csv
                ext2 = self.__fileext[0]
            elif format.lower() == self.__fileext[1]:
                # json-File
                ext2 = self.__fileext[1]
            else:
                return -2 # Das Dateiformat wird nicht unterstützt

        print(folder)
        print(filename)
        print(name, ext)

        print(folder + '\\' + filename, os.path.exists(os.path.join(folder, filename)))

        timestamp = ''
        counterstr = ''
        counter = 0
        if not overwrite:
            # Zeitstempel an Dateiname anhängen
            timestamp = time.strftime("_%Y-%m-%d_%H-%M-%S")
            while os.path.exists(os.path.join(folder,name + timestamp + counterstr + ext2)) and counter < 10000:
                counterstr = f'_{counter:04}'
                counter += 1
            if counter > 9999:
                return -3 # Datei ist shon verhanden
        print("TTTT", folder + '\n' + filename + '\n' + timestamp + '\n' +counterstr + '\n' + ext2)
        if ext2 == self.__fileext[0]:
            r = self._savedatacsv(os.path.join(folder,name + timestamp + counterstr + ext2))
            if r < 0:
                return -4 # Fehler beim Schreiben der Datei afgetreten
        elif ext2 == self.__fileext[1]:
            r = self._savedatajson(os.path.join(folder,name + timestamp + counterstr + ext2))
            if r < 0:
                return -4 # Fehler beim Schreiben der Datei afgetreten
        else:
            return -5 # sollte eigentlich nicht vorkommen

    @property
    def storage(self):
        return self._storage
    
    @storage.setter
    def storage(self, x : bool):
        self._storage = x

x = DataStorage()
x.storage = True
x.adddata("FG", 10)
x.adddata("FG", 10)
#x.adddata('FH', 99)
#x.adddata("FG", 20)
#x.adddata('FI', 99)
#x.adddata("FJ", 20)
#x.adddata("FG", 10)
print(x.savedata("./test1.csv", overwrite = False))
print(x.savedata("./test.json", overwrite = True))
sys.exit()
x.storage = True
x.adddata("FG", 10)
x.adddata('FH', 99)
x.adddata("FG", 20)
x.adddata('FI', 99)
x.adddata("FJ", 20)

print(x.getdata())
print(x.getkeys())
#x.savedata("./test.json")