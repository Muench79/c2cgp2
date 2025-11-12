class DataStorage():
    def __init__(self):
        self._data = {}
    
    def adddata(self, key, value):
        if key not in self._data:
            self._data[key] = [value]
        else:
            self._data[key].append(value)
    
    def getdata(self):
        return self._data

    def getkeys(self):
        return tuple(self._data.keys())

x = DataStorage()

x.adddata("FG", 10)
x.adddata('FG', 99)
print(x.getdata())
print(x.getkeys())