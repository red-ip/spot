# spot_check
Bluetooth presents control for HomeMatic CCU2


Deutsch

Motivation:
Einer Hausautomatisierung der man sagen muss wann man zuhause ist und wann nicht, macht kein Spaß. Mein Leben ist sehr dynamisch und dammit musst die Hausautomatisierung zurechtkommen. Hier zu gibt es zahlreichen Möglichkeiten. Ich habe einiges ausprobiert, aber wirklich zufrieden war ich nie. Danach habe ich gesucht:

Die Lösung darf nicht teuer sein und schon garnicht Monatlich Gebühren kosten.
Die Erkennung muss schnell und zuverlässig funktionieren
Es muss mit beliebig vielen Teilnehmern funktionieren
Es muss mit meiner CCU2 zusammen spielen
Es muss einfach sein und nicht mein Handy Akku belasten.

Da ich immer mein Telefon mit habe, habe ich mich entschieden das ganze über Bluetooth zu realisieren.

Diese Dingen braucht man:

HomeMatic CCU2
XML-API CCU Addon

RASPBERRY PI
Bluetooth Adapter (RASPBERRY PI 3 hat Bluetooth integriert)
Linux (Raspbian, Ubuntu, Debian… )


1# RASPBERRY PI
Bluetooth muss installiert und funktionsbereit sein auf euren Raspberry.
Jedes Gerät muss mit den Raspberry gekoppelt werden. ich bin nach der Anleitung unter den folgenden Link vorgegangen:
http://www.wolfteck.com/projects/raspi/iphone/


2# Erstelle auf der CCU2 für jedes Gerät das Du abfragen willst einer System Variable (Logic value) true = is true, false = is false

Der Name der Variablen: var_spot_CC:23:F5:45:BA:E4_marius_iPhone
Die Variable ist wie folgt aufgebaut :
“var_spot_”		= Hier dran erkennt das Programm die Variable
“CC:23:F5:45:BA:E4”	= das ist die MAC Adresse des Gerät das überprüft werden soll
“_marius"		= Name des Teilnehmers
“_iPhone”		= Gerätename des Teilnehmers


3# kopiere das python Programm in das VZ /opt/spot/

editiere die folgende Datei

