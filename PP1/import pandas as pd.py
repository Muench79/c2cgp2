import pandas as pd
import random
import time

class MessSystem:
    def __init__(self):
        # Datenspeicher
        self.messdaten = {
            "Temperatur": [],
            "Luftfeuchtigkeit": [],
            "Druck": []
        }

    def messe_werte(self):
        """
        Simuliert eine dynamische Messung.
        Hier könnten echte Sensorwerte eingelesen werden!
        """
        temperatur = 20 + random.uniform(-1, 1)
        luftfeuchtigkeit = 45 + random.uniform(-3, 3)
        druck = 1010 + random.uniform(-2, 2)

        return temperatur, luftfeuchtigkeit, druck

    def erfasse_messungen(self, anzahl):
        """
        Führt mehrere Messungen aus und speichert sie in den Listen.
        """
        for i in range(anzahl):
            temperatur, luftfeuchtigkeit, druck = self.messe_werte()

            self.messdaten["Temperatur"].append(temperatur)
            self.messdaten["Luftfeuchtigkeit"].append(luftfeuchtigkeit)
            self.messdaten["Druck"].append(druck)

            print(f"Messung {i+1}: T={temperatur:.2f}°C, LF={luftfeuchtigkeit:.2f}%, P={druck:.2f} hPa")
            time.sleep(0.5)  # simuliert zeitliche Verzögerung

    def exportiere_csv(self, dateiname="messwerte.csv"):
        """
        Speichert die Messwerte in einer CSV-Datei.
        """
        df = pd.DataFrame(self.messdaten)
        df.to_csv(dateiname, index=False)
        print(f"CSV-Datei '{dateiname}' erfolgreich gespeichert!")


# -------------------------------------------
# Nutzung der Klasse
# -------------------------------------------

if __name__ == "__main__":
    messung = MessSystem()          # Objekt erzeugen
    messung.erfasse_messungen(5)    # fünf dynamische Messungen ausführen
    messung.exportiere_csv()        # CSV exportieren
