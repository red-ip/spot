Bluetooth presents control for HomeMatic


Mit “Spot” hast Du eine einfache und zuverlässige Möglichkeit die Anwesenheit von Personen zu prüfen und an deine Haus-Automatisierung weiterzugeben.

Die größten Vorteile sind:
	Alles passiert Lokal ohne Internet und Dienstleister
	Es fallen keine Laufenden Kosten an (ausser Strom)
	Es ist sehr energiesparend (auch für das Telefon)
	Geräteverwaltung passier über die CCU2, daher besonders einfach
	Es lassen sich mehrere Sensoren einbinden, sodass man einen Reichweite von Bluethooth frei skalieren kann.


Welche Komponenten habe ich verwendet:
HomeMatic CCU2 und XML-API CCU Addon
RASPBERRY PI (mit Raspbian)
Bluetooth Adapter (RASPBERRY PI 3 hat Bluetooth integriert - habe es aber nicht getestet)


1# RASPBERRY PI
Bluetooth muss auf dem Raspberry installiert und funktionsbereit sein.
Jedes Gerät muss mit den Raspberry “gekoppelt” werden. ich bin nach der Anleitung unter den folgenden Link vorgegangen (Unter Pairing):
http://www.wolfteck.com/projects/raspi/iphone/

Info : bei mir ist das Telefon mit dem Raspberry nie verbunden. Aber sie haben sich gegenseitig bekanntgemacht - das reicht aus!

Hier die wichtigsten Befehle:
sudo aptitude install bluetooth bluez-utils bluez-compat
hcitool scan						Sucht nach BT Geräten
hcitool dev				                Zeigt den BT Adapter an
bluez-simple-agent hci0 70:48:0F:94:E3:3B		koppelt ein Geräte
bluez-test-device list				        Listet die gekoppelten Geräte an

2# HomeMatic Konfiguration
Erstelle auf der CCU2 für jedes Gerät das Du abfragen willst einer System Variable (Logic value true = is true, false = is false) Englische Schreibweise verwenden

Der Name der Variablen: var_spot_CC:23:F5:45:BA:E4_marius_iPhone
Die Variable ist wie folgt aufgebaut :

“var_spot_”		= dadurch erkennt Spot die Variable, dies bleibt immer gleich
“CC:23:F5:45:BA:E4”	= das ist die MAC Adresse des Gerätes das überprüft werden soll
“_marius"		= Name des Teilnehmers
“_iPhone”		= Gerätename des Teilnehmers


3# Erstelle ein Programme auf der CCU2

Beispiel Anwesenheit :
	System state var_spot_CC:29:F5:57:Bf:1C_marius_iPhone when is true trigger when chenged
	AND 
	System state Anwesenheit when nicht anwesend check only
OR
	System state var_spot_CC:29:C2:17:A4:A2_paulina_iPhone when is true trigger when chenged
	AND 
	System state Anwesenheit when nicht anwesend check only

Activity 
	System state Anwesenheit immediately anwesend
	


Beispiel Keine Anwesenheit :
	System state var_spot_CC:29:F5:57:Bf:1C_marius_iPhone when is false trigger when chenged
AND
	System state var_spot_CC:29:C2:17:A4:A2_paulina_iPhone when is false trigger when chenged

Activity 
	System state Anwesenheit immediately nicht anwesend


(Sorry für die Vermischung der Sprachen)



4# Spot installation auf dem RASPBERRY PI 

sudo mkdir /opt/spot/
sudo chown pi:pi /opt/spot/
- Besorge dir Spot von https://github.com/red-ip/spot/
- und speicher alles unter /opt/spot/

cd /opt/spot/
python spot.py -s	# Testlauf

- editiere die /opt/spot/spot.cfg 
mcedit spot.cfg         ==> ip_ccu = <ip adresse der ccu2 eintragen>

- more /opt/spot/init.d/spot
sudo cp /opt/spot/init.d/spot /etc/init.d
sudo chmod 744 /etc/init.d/spot

- als Service registrieren

- Starte Spot
sudo python spot.py -d		# Hierbei startet Spot auch einen lokalen (Spot-) Sensor


Optional:
Es ist möglich Spot als einen zusätzlich Sensor zu starten um zB die Reichweiten von Bluetooth zu erweitern. Hierfür wird ein weiterer RASPBERRY PI benötigt. Die Einrichtung des Sensors ist identisch mit der bereits oben beschriebenen Einrichtung von Spot bis auf den Aufruf des Programmes. Hierzu muss die folgende Datei editiert werden
/etc/init.d/spot

ändere die Zeile 
COLLECTORD_BIN=/opt/spot/spot.py
zu
COLLECTORD_BIN=/opt/spot/spot_sensor.py

- Starte Spot_sensors
sudo python /opt/spot/spot_sensor.py -d		

Bedenke das Spot nach Sensoren mittels Broadcast sucht, sollten disen sich nicht in der gleichen broadcast Domäne befinden, kannst Spot mit dem Parameter "-m" gefolgt von <IP>:<PORT> eine Liste (Komma getrennt) an Sensoren mitgeben. 

