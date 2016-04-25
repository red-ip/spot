# spot_check
Bluetooth presents control for HomeMatic CCU2


Mit “Sport” hast Du eine einfache und zuverlässige Möglichkeit die Anwesenheit von Personen zu prüfen und an die Haus-Automatisierung weiterzugeben.

Die größten Vorteile sind:
	Alles passiert Lokal ohne Internet und Dienstleister
	Es fallen keine Laufenden Kosten an (ausser Strom)
	Es ist sehr energiesparend (auch für das Telefon)
	Geräteverwaltung passier über die CCU2, daher besonders einfach


Welche Komponenten habe ich verwendet:

HomeMatic CCU2 und XML-API CCU Addon

RASPBERRY PI (mit Raspbian)
Bluetooth Adapter (RASPBERRY PI 3 hat Bluetooth integriert)



1# RASPBERRY PI
Bluetooth muss auf dem Raspberry installiert und funktionsbereit sein.
Jedes Gerät muss mit den Raspberry “gekoppelt” werden. ich bin nach der Anleitung unter den folgenden Link vorgegangen:
http://www.wolfteck.com/projects/raspi/iphone/
Info : bei mir ist das Telefon mit dem Raspberry nie verbunden. Aber sie haben sich gegenseitig bekanntgemacht - das reicht aus

Hier die wichtigsten Befehle:
hcitool scan						Sucht nach BT Geräten
hcitool dev						Zeigt den BT Adapter an
bluez-simple-agent hci0 70:48:0F:94:E3:3B		koppelt ein Geräte
bluez-test-device list					Listet die gekoppelten Geräte an

2# Erstelle auf der CCU2 für jedes Gerät das Du abfragen willst einer System Variable (Logic value true = is true, false = is false)

Der Name der Variablen: var_spot_CC:23:F5:45:BA:E4_marius_iPhone
Die Variable ist wie folgt aufgebaut :
“var_spot_”		= Hier dran erkennt das Programm die Variable, bleibt immer gleich
“CC:23:F5:45:BA:E4”	= das ist die MAC Adresse des Gerät das überprüft werden soll
“_marius"		= Name des Teilnehmers
“_iPhone”		= Gerätename des Teilnehmers

3# Erstelle auf der Programme auf der CCU2


4# Spot installation
sudo mkdir /opt/spot/
sudo chown pi:pi /opt/spot/
unzip -d /opt/spot spot.zip
cd /opt/spot/
python spot.py -s
mcedit spot.cfg         ==> ip_ccu = <ip adresse der ccu2 eintragen>
#more /opt/spot/init.d/spot
sudo cp /opt/spot/init.d/spot /etc/init.d
sudo chmod 744 /etc/init.d/spot
# als Service regestrieren fehlt noch

python spot.py -l -d



---

nmap -p 80,443,1999,2001,8181 -n --open -oN output.txt  192.168.178.0/24


