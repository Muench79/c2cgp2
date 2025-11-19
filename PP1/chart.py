import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import math



df = pd.read_csv('line_test_2025-11-19_07-01-54.csv')
df["time"] = pd.to_datetime(df["time"], unit="s")
df["time_ms"] = (df["time"] - df["time"].iloc[0]).dt.total_seconds()

print(df["time"].dtype)

df_speed = df[['time_ms', 'speed']]
df_speed = df_speed.dropna()
df_infrared_analog_0 = df[['time_ms', 'infrared_analog_0']]
df_infrared_analog_0 = df_infrared_analog_0.dropna()
df_infrared_analog_1 = df[['time_ms', 'infrared_analog_1']]
df_infrared_analog_1 = df_infrared_analog_1.dropna()
df_infrared_analog_2 = df[['time_ms', 'infrared_analog_2']]
df_infrared_analog_2 = df_infrared_analog_2.dropna()
df_infrared_analog_3 = df[['time_ms', 'infrared_analog_3']]
df_infrared_analog_3 = df_infrared_analog_3.dropna()
df_infrared_analog_4 = df[['time_ms', 'infrared_analog_4']]
df_infrared_analog_4 = df_infrared_analog_4.dropna()
df_steering_angle = df[['time_ms', 'steering_angle']]
df_steering_angle = df_steering_angle.dropna()
drive_time = df_speed["time_ms"].iloc[-1] - df_speed["time_ms"].iloc[0]
print(math.ceil(drive_time))
plt.figure(figsize=(15, 8))  # Diagrammgröße festle
plt.step(x=df_speed["time_ms"], y=df_speed["speed"], where="post", label="Geschwindigkeit")
plt.step(x=df_steering_angle["time_ms"], y=df_steering_angle["steering_angle"], where="post", label="Lenkwinkel")
plt.step(x=df_infrared_analog_0["time_ms"], y=df_infrared_analog_0["infrared_analog_0"], where="post", label="IR 0")
plt.step(x=df_infrared_analog_1["time_ms"], y=df_infrared_analog_1["infrared_analog_1"], where="post", label="IR 1")
plt.step(x=df_infrared_analog_2["time_ms"], y=df_infrared_analog_2["infrared_analog_2"], where="post", label="IR 2")
plt.step(x=df_infrared_analog_3["time_ms"], y=df_infrared_analog_3["infrared_analog_3"], where="post", label="IR 3")
plt.step(x=df_infrared_analog_4["time_ms"], y=df_infrared_analog_4["infrared_analog_4"], where="post", label="IR 4")
plt.xlabel("Zeit")
plt.ylabel("Geschwindigkeit")
plt.title("Treppenförmiges Diagramm")
plt.grid(True)
plt.xlabel("Zeit")
plt.ylabel("Geschwindigkeit")
plt.title("Treppenförmiges Diagramm")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1)) 
plt.grid(True)
plt.xticks(ticks=range(0,math.ceil(drive_time) + 1), rotation=45)
plt.tight_layout()
plt.show()
plt.savefig("./zzz2.png")
