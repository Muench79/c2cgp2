from datetime import date, datetime
import csv
import sys
import os

fahrzeuge = []
fahrzeugeDict = {}



# Fahrzeug Klasse
class Fahrzeug:
    def __init__(self, baujahr, erstzulassung, identNr, farbe, marke, kennzeichen): # Initialisierung
        self.baujahr = baujahr
        self.erstzulassung = erstzulassung
        self.identNr = identNr
        self.farbe = farbe
        self.hoehe = 0
        self.breite = 0
        self.laenge = 0
        self.marke = marke
        self.kennzeichen = kennzeichen
        self.fahrtenbuch = []
        self.__fahrtenbuch = []
        self.doNotShowPrivate = True

    def __str__(self): # Rückgabewert von obj.__str__ festlegen
        return f"Fahrzeugdaten: BJ {self.baujahr}, EZ {self.erstzulassung}, ID {self.identNr}, F {self.farbe}"
    
    def __repr__(self): # Rückgabewert von obj.__repr__ festlegen
        return f"FahrzeugidentNr: {self.identNr}"

    def __lt__(self, other): # Vergleichsoperator __lt__ < less than bzw. kleiner als 
        return self.volumen < other.volumen
    
    def __le__(self, other): # Vergleichsoperator __le__ <= less or equal bzw. kleiner oder gleich
        return self.volumen <= other.volumen
    
    def __gt__(self, other): # Vergleichsoperator __gt__ > greater than bzw. größer als
        return self.volumen > other.volumen
    
    def __ge__(self, other): # Vergleichsoperator __ge__ >= greater or equal bzw. größer oder gleich
        return self.volumen >= other.volumen
    
    def __eq__(self, other): # Vergleichsoperator __eq__ == equal bzw. gleich
        return self.volumen == other.volumen
    
    def __ne__(self, other): # Vergleichsoperator __ne__ != not equal bzw. ungleich
        return self.volumen != other.volumen

    def HasFahrerlaubnis(self): # Wird überschrieben
        pass

    def setSize(self, hoehe, breite, laenge): # Maße des Fahrzeugs setzen
        self.hoehe = hoehe
        self.breite = breite
        self.laenge = laenge
    
    def filterSettings(self, doNotShowPrivate):
        self.fahrtenbuch = []
        if doNotShowPrivate:
            for e in self.__fahrtenbuch:
                if not e.privatfahrt:
                    self.fahrtenbuch.append(e)
        else:
            self.fahrtenbuch = self.__fahrtenbuch


    def addJourneyEintrag(self, datum, startort, zielort, kilometer_start, kilommeter_ende, zweck, privatfahrt):
        print(datum, startort, zielort, kilometer_start, kilommeter_ende, zweck, privatfahrt.lower())
        self.__fahrtenbuch.append(Journey(datum, startort, zielort, kilometer_start, kilommeter_ende, zweck, privatfahrt))
        self.filterSettings(self.doNotShowPrivate)

    def get_last_journey(self):
        self.filterSettings(self.doNotShowPrivate)
        try:
            return f"Fahrt am {self.fahrtenbuch[-1].datum.strftime("%d.%m.%Y")} von {self.fahrtenbuch[-1].startort} nach {self.fahrtenbuch[-1].zielort}"
        except:
            return 'Fehler'
    @property
    def volumen(self): # Volumen berechnen und zurückgeben
        return self.hoehe * self.breite * self.laenge

# Pkw Klasse
class Pkw(Fahrzeug): # Erbt von Fahrzeug Klasse
    def __init__(self, baujahr, erstzulassung, identNr, farbe, hubraum, marke, kennzeichen): # Initialisierung
        super().__init__(baujahr, erstzulassung, identNr, farbe, marke, kennzeichen) # Initialisierung der super Klasse
        self.hubraum = hubraum
        
    def __str__(self): # Rückgabewert von obj.__str__ festlegen
        return f"Fahrzeugdaten: BJ {self.baujahr}, EZ {self.erstzulassung}, ID {self.identNr}, F {self.farbe}, HR {self.hubraum}"
    
    def __repr__(self): # Rückgabewert von obj.__repr__ festlegen
        return super().__repr__() +f"FahrzeugidentNr: {self.identNr} (Pkw)"
    
    def hasFahrerlaubnis(self, person): # Fahrerlaubnis der Person  für dieses Fahrzeug abfragen
        return person.alter >= 18
    
class Motorrad(Fahrzeug):
    def __init__(self, baujahr, erstzulassung, identNr, farbe, automatik, marke, kennzeichen): # Initialisierung
        super().__init__(baujahr, erstzulassung, identNr, farbe, marke, kennzeichen) # Initialisierung der super Klasse
        self.automatik = automatik
    
    def __str__(self): # Rückgabewert von obj.__str__ festlegen
        return f"Fahrzeugdaten: BJ {self.baujahr}, EZ {self.erstzulassung}, ID {self.identNr}, F {self.farbe}, A {self.automatik}"
    
    def __repr__(self): # Rückgabewert von obj.__repr__ festlegen
        return super().__repr__() +  f"FahrzeugidentNr: {self.identNr} (Motorrad)"
    
    def hasFahrerlaubnis(self, person): # Fahrerlaubnis der Person  für dieses Fahrzeug abfragen
        return person.alter >= 18
    
class Lkw(Fahrzeug):
    def __init__(self, baujahr, erstzulassung, identNr, farbe, marke, kennzeichen): # Initialisierung
        super().__init__(baujahr, erstzulassung, identNr, farbe, marke, kennzeichen) # Initialisierung der super Klasse
    
    def __str__(self): # Rückgabewert von obj.__str__ festlegen
        return f"Fahrzeugdaten: BJ {self.baujahr}, EZ {self.erstzulassung}, ID {self.identNr}, F {self.farbe}, HR {self.hubraum}"
    
    def __repr__(self): # Rückgabewert von obj.__repr__ festlegen
        return f"FahrzeugidentNr: {self.identNr} (Lkw)"
    
    def hasFahrerlaubnis(self, person): # Fahrerlaubnis der Person  für dieses Fahrzeug abfragen
        return person.alter >= 24

class Person:
    def __init__(self, vorname, nachname, geburtsdatum): # Initialisierung
        self.vorname = vorname
        self.nachname = nachname
        self.geburtsdatum = geburtsdatum
    
    @property
    def alter(self): # Alter der Person berechnen und zurückgeben
        heute = date.today()
        alter = heute.year - self.geburtsdatum.year
        if (heute.month, heute.day) < (self.geburtsdatum.month, self.geburtsdatum.day):
            alter -= 1
        return alter
    def __str__(self): # Rückgabewert von obj.__str__ festlegen
        return f"{self.vorname}, {self.nachname}, {self.geburtsdatum.year}-{self.geburtsdatum.month}-{self.geburtsdatum.day}"
    
    def __repr__(self): # Rückgabewert von obj.__repr__ festlegen
        return f"{self.vorname}, {self.nachname}"
    
# Fahrtenbuch
class Journey:
    def __init__(self, datum, startort, zielort, kilometer_start, kilometer_ende, zweck, privatfahrt):
        self.datum = datetime.strptime(datum, '%d.%m.%Y')
        self.startort = startort
        self.zielort = zielort
        self.kilometer_start = int(kilometer_start)
        self.kilometer_ende = int(kilometer_ende)
        self.zweck = zweck
        self.privatfahrt = (privatfahrt.lower() == 'ja')
    
    @property
    def distanz(self):
        return self.kilometer_ende - self.kilometer_start


with open(r'D:\Users\martenjo\OneDrive - Volkswagen AG\Desktop\C2C\fahrzeuge.csv', encoding='utf-8') as fFahrzeuge:
    fCsvDaten = csv.DictReader(fFahrzeuge)
    for row in fCsvDaten:
        if row['TYP'].lower() == 'pkw':
            fahrzeuge.append(Pkw(row['BJ'], row['EZ'], row['ID'],'','', row['MARKE'] , row['KENNZEICHEN']))
            fahrzeugeDict[row['ID']] = Pkw(row['BJ'], row['EZ'], row['ID'],'','', row['MARKE'], row['KENNZEICHEN'] )
        elif row['TYP'].lower() == 'lkw':
            fahrzeuge.append(Lkw(row['BJ'], row['EZ'], row['ID'],'', row['MARKE'], row['KENNZEICHEN'] ))
            fahrzeugeDict[row['ID']] = Lkw(row['BJ'], row['EZ'], row['ID'],'', row['MARKE'], row['KENNZEICHEN'] )



for fzg in fahrzeuge:
    if os.path.exists('C:\\Users\\martenjo\OneDrive - Volkswagen AG\\Desktop\\C2C\\Fahrtenbücher\\' + fzg.kennzeichen + '.csv'):
        with open('C:\\Users\\martenjo\OneDrive - Volkswagen AG\\Desktop\\C2C\\Fahrtenbücher\\' + fzg.kennzeichen + '.csv', encoding='utf-8') as fj:
            csvDaten = csv.reader(fj)   
            for row in csvDaten:
                datum, startort, zielort, kilometer_start, kilometer_ende, zweck, privatfahrt = row
                fzg.addJourneyEintrag(datum, startort, zielort, kilometer_start, kilometer_ende, zweck, privatfahrt)

for fzg in fahrzeuge:
    if fzg.kennzeichen == 'IN-AD-1':
        for j in fzg.fahrtenbuch:
            print(j.distanz)
        print(fzg.get_last_journey())
sys.exit()
print(fahrzeuge[0].kennzeichen)
print(fahrzeugeDict)
fahrzeuge[0].addJourneyEintrag('1.5.2021','Wolfsburg','Hannover','40100','40185','Warenlieferung','nein')
sys.exit()

f1 = Fahrzeug('2025', '2025', 6666, 'rot')
f2 = Fahrzeug('2025', '2025', 6666, 'rot')
p1 = Person('Alex', 'Muster', date(2017, 12, 8))
print(p1.alter)
audi = Pkw(94, 94, 122333, 'grün',1500)
audi2 = Pkw(94, 94, 123334, 'grün',1500)
print('FFFF', "Berechtigt" if audi.hasFahrerlaubnis(p1) else 'nicht berechtigt')
print(audi)
audi.setSize(1,2,3)
audi2.setSize(1,2,2)
print(audi.volumen)

print(audi > audi2)
print(audi < audi2)
print(audi == audi2)
print(audi != audi2)
print(p1)
print(f1 < f2)