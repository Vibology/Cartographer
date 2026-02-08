"""
Pydantic schemas for Synthesis endpoints (combined Astrology + HD)
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SynthesisRequest(BaseModel):
    name: str = Field(..., description="Person's name")
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    tz_str: str = Field(..., description="Timezone")
    place: Optional[str] = Field(None, description="Place name for HD calculation")
    house_system: str = Field("P", description="Astrology house system")

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
                "place": "New York, USA",
                "house_system": "P"
            }
        }

class SynthesisResponse(BaseModel):
    name: str
    birth_data: Dict[str, Any]
    astrology: Dict[str, Any]
    human_design: Dict[str, Any]
    synthesis_notes: Dict[str, str]
