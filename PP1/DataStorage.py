import time

class DataStorage():
    def __init__(self, storage : bool = False):
        self._data = {}
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
    
    @property
    def storage(self):
        return self._storage
    
    @storage.setter
    def storage(self, x : bool):
        self._storage = x

x = DataStorage()

x.adddata("FG", 10)
x.adddata('FG', 99)
print(x.getdata())
print(x.getkeys())