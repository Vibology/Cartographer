"""
Pydantic schemas for Astrology endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum

class ChartFormat(str, Enum):
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"

class AstrologyCalculateRequest(BaseModel):
    name: str = Field(..., description="Person's name")
    year: int = Field(..., ge=1900, le=2100, description="Birth year")
    month: int = Field(..., ge=1, le=12, description="Birth month")
    day: int = Field(..., ge=1, le=31, description="Birth day")
    hour: int = Field(..., ge=0, le=23, description="Birth hour (24h format)")
    minute: int = Field(..., ge=0, le=59, description="Birth minute")
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    tz_str: str = Field(..., description="Timezone string (e.g., 'America/New_York')")
    house_system: str = Field("P", description="House system: P=Placidus, W=Whole Sign, K=Koch, etc.")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Example Person",
                "year": 1990,
                "month": 1,
                "day": 15,
                "hour": 12,
                "minute": 30,
                "lat": 40.7128,
                "lng": -74.0060,
                "tz_str": "America/New_York",
                "house_system": "P"
            }
        }

class PlanetPosition(BaseModel):
    name: str
    sign: str
    longitude: float
    latitude: float
    speed: float
    retrograde: bool
    house: int

class AspectData(BaseModel):
    planet1: str
    planet2: str
    aspect: str
    orb: float
    applying: bool

class AstrologyCalculateResponse(BaseModel):
    name: str
    birth_data: Dict[str, Any]
    planets: List[PlanetPosition]
    houses: Dict[str, float]
    aspects: List[AspectData]
    lunar_phase: Dict[str, Any]
    elements: Dict[str, int]
    modalities: Dict[str, int]
