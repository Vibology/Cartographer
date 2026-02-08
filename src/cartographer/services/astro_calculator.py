"""
Astrology Calculation Service - Kerykeion wrapper
"""

from kerykeion import AstrologicalSubject
from datetime import datetime
import pytz

def calculate_natal_chart(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lng: float,
    tz_str: str,
    house_system: str = "P"
):
    """
    Calculate complete natal chart using Kerykeion.

    Returns dictionary with planets, houses, aspects, etc.
    """
    # Create AstrologicalSubject
    subject = AstrologicalSubject(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        lat=lat,
        lng=lng,
        tz_str=tz_str,
        city="",  # Not needed if we have lat/lng
        nation="",
        zodiac_type="Tropic",
        online=False  # Use local ephemeris
    )

    # Build response
    planets_data = []
    for planet in subject.planets_list:
        planets_data.append({
            "name": planet["name"],
            "sign": planet["sign"],
            "longitude": planet["position"],
            "latitude": planet.get("latitude", 0.0),
            "speed": planet.get("speed", 0.0),
            "retrograde": planet.get("retrograde", False),
            "house": planet.get("house", 0)
        })

    houses_data = {}
    for i, cusp in enumerate(subject.houses_list, 1):
        houses_data[f"house_{i}"] = cusp["position"]

    aspects_data = []
    for aspect in subject.aspects_list:
        aspects_data.append({
            "planet1": aspect["p1_name"],
            "planet2": aspect["p2_name"],
            "aspect": aspect["aspect"],
            "orb": aspect["orbit"],
            "applying": aspect.get("applying", False)
        })

    # Element and modality distribution
    elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    modalities = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}

    element_map = {
        "Ari": "Fire", "Leo": "Fire", "Sag": "Fire",
        "Tau": "Earth", "Vir": "Earth", "Cap": "Earth",
        "Gem": "Air", "Lib": "Air", "Aqu": "Air",
        "Can": "Water", "Sco": "Water", "Pis": "Water"
    }

    modality_map = {
        "Ari": "Cardinal", "Can": "Cardinal", "Lib": "Cardinal", "Cap": "Cardinal",
        "Tau": "Fixed", "Leo": "Fixed", "Sco": "Fixed", "Aqu": "Fixed",
        "Gem": "Mutable", "Vir": "Mutable", "Sag": "Mutable", "Pis": "Mutable"
    }

    for planet in planets_data:
        sign_abbr = planet["sign"][:3]
        if sign_abbr in element_map:
            elements[element_map[sign_abbr]] += 1
        if sign_abbr in modality_map:
            modalities[modality_map[sign_abbr]] += 1

    return {
        "name": name,
        "birth_data": {
            "date": f"{year}-{month:02d}-{day:02d}",
            "time": f"{hour:02d}:{minute:02d}",
            "location": {"lat": lat, "lng": lng, "timezone": tz_str}
        },
        "planets": planets_data,
        "houses": houses_data,
        "aspects": aspects_data,
        "lunar_phase": {
            "phase": subject.lunar_phase.get("moon_phase", "Unknown"),
            "illumination": subject.lunar_phase.get("illumination", 0)
        },
        "elements": elements,
        "modalities": modalities
    }

def calculate_current_transits(lat: float, lng: float, tz_str: str):
    """Calculate current planetary positions (transits)."""
    now = datetime.now(pytz.timezone(tz_str))

    subject = AstrologicalSubject(
        name="Current Transits",
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        lat=lat,
        lng=lng,
        tz_str=tz_str,
        city="",
        nation="",
        zodiac_type="Tropic",
        online=False
    )

    transits = []
    for planet in subject.planets_list:
        transits.append({
            "planet": planet["name"],
            "sign": planet["sign"],
            "longitude": planet["position"],
            "retrograde": planet.get("retrograde", False)
        })

    return {
        "timestamp": now.isoformat(),
        "location": {"lat": lat, "lng": lng, "timezone": tz_str},
        "transits": transits
    }
