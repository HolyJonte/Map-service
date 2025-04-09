import requests

API_KEY = "a8f74965f0784d1297d38c4fc295120c"
BASE_URL = "https://api.trafikinfo.trafikverket.se/v2/data.json"
HEADERS = {"Content-Type": "application/xml"}

def fetch_cameras():
    body = f"""
    <REQUEST>
        <LOGIN authenticationkey="{API_KEY}" />
        <QUERY objecttype="TrafficSafetyCamera" schemaversion="1.0">
            <INCLUDE>Id</INCLUDE>
            <INCLUDE>Name</INCLUDE>
            <INCLUDE>Geometry</INCLUDE>
        </QUERY>
    </REQUEST>
    """
    response = requests.post(BASE_URL, headers=HEADERS, data=body.strip())
    print("STATUSKOD:", response.status_code)
    print("SVAR FRÅN API:")
    print(response.text)
    response.raise_for_status()
    return response.json()




def fetch_accidents():
    body = f"""
    <REQUEST>
        <LOGIN authenticationkey="{API_KEY}" />
        <QUERY objecttype="Situation">
            <FILTER>
                <EQ name="Type" value="Accident"/>
            </FILTER>
        </QUERY>
    </REQUEST>
    """
    response = requests.post(BASE_URL, headers=HEADERS, data=body.strip())
    print("STATUSKOD:", response.status_code)
    print("SVAR FRÅN API:")
    print(response.text)
    response.raise_for_status()
    return response.json()
