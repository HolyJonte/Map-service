from api.fetch_data import fetch_cameras, fetch_situations

def get_all_cameras():
    data = fetch_cameras()
    cameras = []

    for cam in data["RESPONSE"]["RESULT"][0]["TrafficSafetyCamera"]:
        if "Geometry" in cam and cam["Geometry"]:
            geom = cam["Geometry"]["WGS84"]
            lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())
            cameras.append({
                "lat": lat,
                "lng": lng,
                "name": cam.get("Name", "Okänd kamera"),
                "road": cam.get("RoadNumber", "Okänt vägnummer")
            })
    return cameras


def get_all_roadworks():
    data = fetch_situations()
    roadworks = []

    for situation in data["RESPONSE"]["RESULT"][0]["Situation"]:
        for deviation in situation.get("Deviation", []):
            if deviation.get("MessageType") != "Vägarbete":
                continue
            geom = deviation.get("Geometry", {}).get("Point", {}).get("WGS84")
            if geom:
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())
                roadworks.append({
                    "lat": lat,
                    "lng": lng,
                    "message": deviation.get("Message", "Inget meddelande"),
                    "location": deviation.get("LocationDescriptor", "Okänd plats"),
                    "severity": deviation.get("SeverityText", "Okänd påverkan"),
                    "start": deviation.get("StartTime"),
                    "end": deviation.get("EndTime")
                })
    return roadworks


def get_all_accidents():
    data = fetch_situations()
    accidents = []

    for situation in data["RESPONSE"]["RESULT"][0]["Situation"]:
        for deviation in situation.get("Deviation", []):
            if deviation.get("MessageType") != "Olycka":
                continue
            geom = deviation.get("Geometry", {}).get("Point", {}).get("WGS84")
            if geom:
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())
                accidents.append({
                    "lat": lat,
                    "lng": lng,
                    "message": deviation.get("Message", "Ingen beskrivning"),
                    "start": deviation.get("StartTime"),
                    "end": deviation.get("EndTime"),
                    "severity": deviation.get("SeverityText", "Okänd påverkan"),
                    "location": deviation.get("LocationDescriptor", "Okänd plats")
                })
    return accidents

# Här har vi en funktion som hämtar olycksdata MED länsfiltrering som borde fungera i stället
# för ovanstående get_all_accidents-funktionen?

""" def get_accidents_data():
    data = fetch_situations()  # Hämtar all data från Trafikverket
    accidents = []
    for situation in data["RESPONSE"]["RESULT"][0]["Situation"]:
        
        # Loopa över alla deviation-objekt i situationen
        for deviation in situation.get("Deviation", []):
            if deviation.get("MessageType") != "Olycka":
                continue

            # Hämta county från deviation istället för situation
            county = deviation.get("CountyNo", None)

            geom = deviation.get("Geometry", {}).get("Point", {}).get("WGS84")
            if not geom:
                continue
            try:
                lat, lng = map(float, geom.replace("POINT (", "").replace(")", "").split())
            except ValueError:
                continue
            accidents.append({
                "lat": lat,
                "lng": lng,
                "message": deviation.get("Message", "Ingen beskrivning"),
                "start": deviation.get("StartTime"),
                "end": deviation.get("EndTime"),
                "severity": deviation.get("SeverityText", "Okänd påverkan"),
                "location": deviation.get("LocationDescriptor", "Okänd plats"),
                "county": county
            })
    return accidents
 """