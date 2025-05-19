För att installera alla beroenden, kör följande kommando i terminalen i Python Anywhere:

För att hamna i rätt mapp i terminalen, kör:
cd ~/Map-service

För installation av alla requirments koden är beroende av, kör:
python3.12 -m pip install --user -r requirements.txt

För samma requirments fast på lokal dator:
py -3.12 -m pip install --user -r requirements.txt

För att hämta de senaste ändringarna från GitHub, kör följande kommando i terminalen:
git pull

Tryck Ctrl + O (för att skriva ut filen)
Tryck Enter (bekräfta filnamnet)
Tryck Ctrl + X (för att avsluta nano)

VIKTIGT!!!
Varje gång man har gjort en uppdatering i CSS koden måste man ändra versionsnummer.
Detta görs i base.html på den raden där CSS filen laddas in, skriv v=+1 från tidigare nr.

För att titta vad som finns i databasen varesig lokalt eller på PA, kör:
python inspect_db.py

För att visa förhandsgranskning av en inbäddad karta gå in på följande länk:
https://h23vicno.pythonanywhere.com/

===========================================================
För att testa sms och email på sidan:
===========================================================
cd ~/map-service
python3 prenumerationsmodul/notifications.py





===========================================================
Dessa används sparsamt:
===========================================================
För att lösa fel med lokala ändringar i tex databasen, kör följande kommando i terminalen:
git reset --hard HEAD
git clean -fd

För att tömma databasen på gammal data som redan är borttagen, kör:
import sqlite3
conn = sqlite3.connect("trafikvida.db")
conn.execute("VACUUM")
conn.close()
