def extract_row(data: dict):

    entry = (data.get("list") or [{}])[0]

    main = entry.get("main", {})
    components = entry.get("components", {})
    coordinates = data.get("coordinates",{})

    return {
        "city": data.get("city"),
        "country": data.get("country"),
        "latitude": coordinates.get("latitude"),
        "longitude": coordinates.get("longitude"),
        "timestamp_utc": data.get("timestamp"),
        "aqi": main.get("aqi"),
        "co": components.get("co"),
        "no": components.get("no"),
        "no2": components.get("no2"),
        "o3": components.get("o3"),
        "so2": components.get("so2"),
        "nh3": components.get("nh3"),
        "pm25": components.get("pm2_5"),
        "pm10": components.get("pm10"),
    }