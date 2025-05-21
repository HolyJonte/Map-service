# Denna fil hanterar API-anrop till Trafikverkets öppna data
# Data hämtas via XML-baserade POST-förfrågningar och returneras i JSON-format

# Importerar requests för att kunna göra HTTP-anrop
import requests
from dotenv import load_dotenv
import os

# Laddar miljövariabler från .env-filen
load_dotenv()

# Vår API-nyckel från Trafikverket (finns i .env-filen)
API_KEY = os.getenv("TRAFIKVERKET_API_KEY")

# Grund-URL till Trafikverkets API
BASE_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"

# HTTP-header för att tala om att vi skickar XML-data
HEADERS = {"Content-Type": "application/xml"}

# Funktion för att hämta fartkameror
def fetch_cameras():
    body = f"""
    <REQUEST>
        <LOGIN authenticationkey="{API_KEY}" />
        <QUERY objecttype="TrafficSafetyCamera" schemaversion="1.0">
            <INCLUDE>Id</INCLUDE>
            <INCLUDE>Name</INCLUDE>
            <INCLUDE>Geometry</INCLUDE>
            <INCLUDE>RoadNumber</INCLUDE>
        </QUERY>
    </REQUEST>
    """

    # Skickar POST-förfrågan till Trafikverkets API
    response = requests.post(BASE_URL, headers=HEADERS, data=body.strip())
    response.raise_for_status()
    return response.json()

# Funktion som hämtar alla trafikrelaterade situationer (vägarbeten, olyckor m.m.) från Trafikverkets API
def fetch_situations():
    body = f"""
    <REQUEST>
        <LOGIN authenticationkey="{API_KEY}" />
        <QUERY objecttype="Situation" namespace="road.trafficinfo" schemaversion="1.5">
            <INCLUDE>Deviation</INCLUDE>
        </QUERY>
    </REQUEST>
    """

    # Skickar POST-förfrågan till Trafikverkets API med XML-bodyn och rätt headers
    response = requests.post(BASE_URL, headers=HEADERS, data=body.strip())
    # Om API-anropet inte lyckas (t.ex. fel API-nyckel eller nätverksfel) kastas ett fel
    response.raise_for_status()
    # Returnerar svaret från API:et i JSON-format
    return response.json()










