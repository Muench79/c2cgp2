import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd




df = pd.read_csv('line_test_2025-11-18_13-51-58.csv')
df["time"] = pd.to_datetime(df["time"])

print(df["time"].dtype)

df_speed = df[['time', 'speed']]
df_speed = df_speed.dropna()
df_infrared_analog_0 = df[['time', 'infrared_analog_0']]
df_infrared_analog_0 = df_infrared_analog_0.dropna()
df_infrared_analog_1 = df[['time', 'infrared_analog_1']]
df_infrared_analog_1 = df_infrared_analog_1.dropna()
df_infrared_analog_2 = df[['time', 'infrared_analog_2']]
df_infrared_analog_2 = df_infrared_analog_2.dropna()
df_infrared_analog_3 = df[['time', 'infrared_analog_3']]
df_infrared_analog_3 = df_infrared_analog_3.dropna()
df_infrared_analog_4 = df[['time', 'infrared_analog_4']]
df_infrared_analog_4 = df_infrared_analog_4.dropna()
df_steering_angle = df[['time', 'steering_angle']]
df_steering_angle = df_steering_angle.dropna()

plt.step(x=df_speed["time"], y=df_speed["speed"], where="post")
plt.step(x=df_steering_angle["time"], y=df_steering_angle["steering_angle"], where="post", label="Stee")
plt.step(x=df_infrared_analog_0["time"], y=df_infrared_analog_0["infrared_analog_0"], where="post")
plt.step(x=df_infrared_analog_1["time"], y=df_infrared_analog_1["infrared_analog_1"], where="post")
plt.step(x=df_infrared_analog_2["time"], y=df_infrared_analog_2["infrared_analog_2"], where="post")
plt.step(x=df_infrared_analog_3["time"], y=df_infrared_analog_3["infrared_analog_3"], where="post")
plt.step(x=df_infrared_analog_4["time"], y=df_infrared_analog_4["infrared_analog_4"], where="post")
plt.xlabel("Zeit")
plt.ylabel("Geschwindigkeit")
plt.title("Treppenförmiges Diagramm")
plt.grid(True)
plt.xlabel("Zeit")
plt.ylabel("Geschwindigkeit")
plt.title("Treppenförmiges Diagramm")
plt.legend()
plt.grid(True)
plt.show()
plt.savefig("./zzz.png")
