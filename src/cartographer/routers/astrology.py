"""
Astrology Router - Western Astrology Calculations and Chart Generation
Using Kerykeion library with Swiss Ephemeris
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import Response
from typing import Optional
from datetime import datetime

from ..schemas.astrology import (
    AstrologyCalculateRequest,
    AstrologyCalculateResponse,
    ChartFormat
)
from ..services.astro_calculator import calculate_natal_chart
from ..services.astro_renderer import render_natal_chart

router = APIRouter()

@router.post("/calculate", response_model=AstrologyCalculateResponse)
async def calculate_astrology(request: AstrologyCalculateRequest):
    """
    Calculate complete Western astrology natal chart.

    Returns:
    - Planetary positions (longitude, latitude, speed, retrograde)
    - House cusps and system
    - Aspects between planets
    - Dignities and receptions
    - Lunar phase and nodes
    """
    try:
        result = calculate_natal_chart(
            name=request.name,
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            lat=request.lat,
            lng=request.lng,
            tz_str=request.tz_str,
            house_system=request.house_system
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/chart")
async def generate_chart(
    name: str = Query(..., description="Person's name"),
    year: int = Query(..., description="Birth year"),
    month: int = Query(..., ge=1, le=12, description="Birth month (1-12)"),
    day: int = Query(..., ge=1, le=31, description="Birth day"),
    hour: int = Query(..., ge=0, le=23, description="Birth hour (0-23)"),
    minute: int = Query(..., ge=0, le=59, description="Birth minute"),
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    tz_str: str = Query(..., description="Timezone (e.g., 'America/New_York')"),
    format: ChartFormat = Query(ChartFormat.PNG, description="Output format"),
    house_system: str = Query("P", description="House system (P=Placidus, W=Whole Sign, etc.)"),
    city: str = Query(None, description="City name (optional, will reverse geocode if not provided)")
):
    """
    Generate natal chart visualization.

    Returns chart image in requested format (PNG, SVG, or PDF).
    """
    try:
        image_data, media_type = render_natal_chart(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            lat=lat,
            lng=lng,
            tz_str=tz_str,
            output_format=format.value,
            house_system=house_system,
            city=city
        )
        return Response(content=image_data, media_type=media_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transits")
async def current_transits(
    lat: float = Query(0.0, description="Observer latitude"),
    lng: float = Query(0.0, description="Observer longitude"),
    tz_str: str = Query("UTC", description="Observer timezone")
):
    """
    Calculate current planetary positions (transits) for given location.

    Returns current positions of all planets, Moon nodes, and Chiron.
    """
    try:
        from ..services.astro_calculator import calculate_current_transits
        result = calculate_current_transits(lat=lat, lng=lng, tz_str=tz_str)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
