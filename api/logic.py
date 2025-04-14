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
