import pandas as pd

speed = 20
steering_angel = 90
direction = 1
ultrasonic = 100
timestamp = 10


data_storage = {"timestamp":[],"speed":[], "direction": [], "steering_angle":[], "ultrasonic":[]}
daten_log = {}

df = pd.Dataframe(data_storage)
#self.parameterspeicher
'''
class dst():
    def __init__():
        self.value_to_log = ["timestamp","speed", "direction", "steering_angle", "ultrasonic"]
        self.data_storage = {}
            if column in self.value_to_log:
                self.data_storage["speed"].append(i)
                pass
            else:
                self.datastorage[column] = []
        print(self.data_storage)
'''
#   def drive_parkour_1(self):
for i in range(20):
    data_storage["timestamp"].append(i)
    data_storage["speed"].append(i)
    data_storage["direction"].append(i)
    data_storage["steering_angle"].append(i)
    data_storage["ultrasonic"].append(i)

df = pd.Dataframe(data_storage)

#    def save_log(self):
#df = pd.DataFrame.from_dict(data_storage, columns= data_storage.keys())
df.to_csv("data_storage.csv", index=False)

#car = BaseCar()
#car.drive_parkour_1()


            


'''
class Datastorage():
    def __init__(self):
        pass

    def write_to_log(self, **kwargs)
        
    def save_log(self):
        pass
'''
