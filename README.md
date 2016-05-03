Bluetooth presents control for HomeMatic


Mit “Spot” hast Du eine einfache und zuverlässige Möglichkeit die Anwesenheit von Personen zu prüfen und an deine Haus-Automatisierung weiterzugeben.

Die größten Vorteile sind:
	Alles passiert Lokal ohne Internet ,Dienstleister und VPN
	Es fallen keine Laufenden Kosten an (ausser Strom)
	Es ist sehr energiesparend (auch für das Telefon)
	Geräteverwaltung passier über die CCU2, daher besonders einfach
	Es lassen sich mehrere Sensoren einbinden, sodass man die Reichweite von Bluetooth frei skalieren kann.
	Protokollierung der Anwesenheit
	Alles ist in Python geschrieben

Welche Komponenten habe ich verwendet:
HomeMatic CCU2 und XML-API CCU Addon
RASPBERRY PI (mit RASPBIAN JESSIE)
Bluetooth Adapter (RASPBERRY PI 3 hat Bluetooth integriert - habe es aber nicht getestet)

Funktionsweise:
Spot ist ein Programm das in Python geschrieben ist, damit läuft es praktisch auf jeder Platform, jedoch ist meine Anleitung auf dem RASPBERRY PI mit "RASPBIAN JESSIE" als Betriebsystem beschränkt. Spot besteht aus zwei Teilen, einem Server und einer beliebigen Anzahl an Sensoren. Der Server hat die Aufgabe mit der HomeMatic CCU zu kommunizieren und die Bluetooth Geräte, die Du überwachen willst an seine Sensoren zu schicken. Die Sensoren arbeiten die Listen mit den Bluetooth Geräte dann ab. Über eine Konfigurationsdatei kannst Du die wichtigsten Einstellungen wie zB die IP Adresse der HomeMatic CCU konfigurieren. Ich denke es macht Sinn das Telefon abzufragen, denn heutzutage haben wir es immer mit uns und jedes Telefon besitzt Bluetooth. In der WEBGUI deiner CCU bestimmst Du welche Geräte überwacht werden sollen.




1# RASPBERRY PI
Bluetooth muss auf dem Raspberry installiert und funktionsbereit sein.
dazu die folgenden Pakete installieren.
sudo su
apt-get install bluetooth mc python-bluez

Jetzt koppeln wie das Telefon mit dem Raspberry

bluetoothctl		startet das Verwaltungsprogramm 
power on		

- Bring dein Telefon in den Status so das andere Geräte es pre BT erkennen können. Bei einen iPhone genügt es in die Bluetooth Enstellungen zu gehen. Solange BT eingeschaltet ist und sein Bildschirm an ist, kann das iPhone erkannt werden.
- um  die MAC Adresse herausfinden, scannen wir die Umgebung : 
scan on			suche nach dem iPhone. 
Ausgabe:
Discovery started
[CHG] Controller 00:15:83:E5:79:36 Discovering: yes
[NEW] Device 5E:7F:77:E1:D5:B5 5E-7F-77-E1-D5-B5
[NEW] Device 4F:17:D2:BD:06:51 4F-17-D2-BD-06-51
[NEW] Device 88:C6:26:65:90:C2 88-C6-26-65-90-C2
[NEW] Device 41:04:EB:57:28:77 41-04-EB-57-28-77
[NEW] Device 11:E7:77:74:17:EB 11-E7-77-74-17-EB
[NEW] Device CC:29:F5:67:B7:EC CC-29-F5-67-B7-EC
[CHG] Device CC:29:F5:67:B5:EC Name: iPhoneMarius
[CHG] Device CC:29:F5:67:B5:EC Alias: iPhoneMarius
[CHG] Device CC:29:F5:67:B5:EC UUIDs:
	00001200-0000-1000-8000-00805f0b34fb
	0000111f-0000-1000-8000-00805f0b34fb
	0000112f-0000-1000-8000-00805f0b34fb
	0000110a-0000-1000-8000-00805f0b34fb
	0000110c-0000-1000-8000-00805f0b34fb
	00001116-0000-1000-8000-00805f0b34fb
	00001132-0000-1000-8000-00805f0b34fb
	00000000-deca-fade-deca-deafdecacafe
	2d8d2466-e14d-451c-88bc-7301abea291a

- Mein Telefon ist iPhoneMarius, und die MAC-Adresse lautet CC:29:F5:67:B5:EC
- Damit sind wir in der Lage das iPhone jetzt zu koppeln

agent on
pair CC:29:F5:67:B5:EC		Telefon muss sich in “discovery modus” befinden

[bluetooth]# pair CC:29:F5:67:B5:EC 
Attempting to pair with CC:29:F5:67:B5:EC
[CHG] Device CC:29:F5:67:B5:EC Connected: yes
Request confirmation
[agent] Confirm passkey 476717 (yes/no): yes
[CHG] Device CC:29:F5:67:B5:EC Modalias: bluetooth:v004Cp6E00d0930
[CHG] Device CC:29:F5:67:B5:EC UUIDs:
	00000000-deca-fade-deca-deafdecacafe
	00001000-0000-1000-8000-00805f0b34fb
	0000110a-0000-1000-8000-00805f0b34fb
	0000110c-0000-1000-8000-00805f0b34fb
	0000110e-0000-1000-8000-00805f0b34fb
	00001116-0000-1000-8000-00805f0b34fb
	0000111f-0000-1000-8000-00805f0b34fb
	0000112f-0000-1000-8000-00805f0b34fb
	00001132-0000-1000-8000-00805f0b34fb
	00001200-0000-1000-8000-00805f0b34fb
[CHG] Device CC:29:F5:67:B5:EC Paired: yes
Pairing successful

exit

Jedes Gerät muss mit den Raspberry “gekoppelt” werden. ich bin nach der Anleitung unter den folgenden Link vorgegangen 
https://wiki.archlinux.org/index.php/Bluetooth
Bei Verwendung von mehreren Raspberry's (Spot-Sensor) muss das Telefon an jeden Raspberry für sich gekoppelt werden


Damit das ganze auch nach einem Neustart zuverlässig funktioniert, muss eine Datei erstellt werden 
mcedit /etc/udev/rules.d/10-local.rules

mit dem folgenden Inhalt:
 # Set bluetooth power up
ACTION=="add", KERNEL=="hci0", RUN+="/usr/bin/hciconfig hci0 up"


1# HomeMatic Konfiguration
Erstelle auf der CCU2 für jedes Gerät das Du abfragen willst einer System Variable (Logic value true = is true, false = is false) Englische Schreibweise verwenden

Der Name der Variablen: var_spot_CC:29:F5:67:B5:EC_marius_iPhone
Die Variable ist wie folgt aufgebaut :

“var_spot_”		= dadurch erkennt Spot die Variable, dies bleibt immer gleich
“CC:29:F5:67:B5:EC”	= das ist die Bluethooth MAC Adresse des Gerätes das überprüft werden soll
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

