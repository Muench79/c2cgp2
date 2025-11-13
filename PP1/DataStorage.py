import time
import json
import os
import sys
import pprint

class DataStorage():
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
    
    def _datapreparation(self):
        self._dataprepared = []
        print(self._data)
        for k, v in self._data.items():
            print(k, v)
            for t in v:
                print(t, v)
                self._dataprepared.append({"data_key" : k, "data_time" : t[0], "data_measurement_value" : t[1]})
        if len(self._dataprepared) > 1:
            print("jjj",self._dataprepared)
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
                print('ich wurde gespeichet')
        except:
            return -1
        return 0

    def savedata(self, path, format = None, overwrite = False):
        p, e = os.path.splitext(path)
        print(os.path.split(path))
        tmppath = path
        print('öööööö', p, e)
        if not os.path.isdir(os.path.split(path)[0]):
            print('Dieser Pfad existiert nicht.')
            return -1
        elif not format:
            if e == '':
                tmppath = path + '.csv'
            elif e.lower() == '.csv':
                tmppath = path
            elif e.lower() == '.json':
                tmppath = path
            else:
                return 2
        else:
            if format.lower() == 'csv':
                if e.lower() == '.csv':
                    tmppath = path
                else:
                    tmppath = path + '.csv'
            elif format.lower() == 'json':
                if e.lower() == '.json':
                    tmppath = path
                else:
                    tmppath = path + '.json'
            else:
                return 2
        p, e = os.path.splitext(tmppath)
        if e.lower() == '.csv':
            x = self._savedatacsv(tmppath)
            print('Ergebnis', x)
        elif e.lower() == '.json':
            self._savedatajson(tmppath)
        else:
            return -3
        
    @property
    def storage(self):
        return self._storage
    
    @storage.setter
    def storage(self, x : bool):
        self._storage = x

x = DataStorage()
x.storage = True
x.adddata("FG", 10)
#x.adddata("FG", 10)
#x.adddata('FH', 99)
#x.adddata("FG", 20)
#x.adddata('FI', 99)
#x.adddata("FJ", 20)
#x.adddata("FG", 10)
x.savedata("./test.json")
x.savedata("./test.csv")
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