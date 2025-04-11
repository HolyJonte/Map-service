# Denna fil hanterar API-anrop till Trafikverkets öppna data
# Data hämtas via XML-baserade POST-förfrågningar och returneras i JSON-format

# Importerar requests för att kunna göra HTTP-anrop
import requests

# Vår API-nyckel från Trafikverket
API_KEY = "a8f74965f0784d1297d38c4fc295120c"

# Grund-URL till Trafikverkets API
BASE_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"

# HTTP-header flr att tala om att vi skickar XML-data
HEADERS = {"Content-Type": "application/xml"}

# Funktion för att hämta fartkameror
def fetch_cameras():
    # XML-bodyy för att hämta fartkameror med Id, namn och geometri
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





def fetch_roadworks():
    body = f"""
    <REQUEST>
        <LOGIN authenticationkey="{API_KEY}" />
        <QUERY objecttype="Situation" namespace="road.trafficinfo" schemaversion="1.5">
        <FILTER></FILTER>
        </QUERY>
    </REQUEST>
    """
    response = requests.post(BASE_URL, headers=HEADERS, data=body.strip())
    response.raise_for_status()
    return response.json()









