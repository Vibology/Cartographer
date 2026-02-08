"""
Synthesis Router - Combined Astrology + Human Design Archetypal Portraits
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from ..schemas.synthesis import SynthesisRequest, SynthesisResponse
from ..services.astro_calculator import calculate_natal_chart
from .. import features as hd

router = APIRouter()

@router.post("/complete", response_model=SynthesisResponse)
async def synthesize_complete_chart(request: SynthesisRequest):
    """
    Generate complete archetypal portrait combining:
    - Western Astrology (planets, houses, aspects)
    - Human Design (type, strategy, authority, profile, gates, channels)

    Returns unified JSON with both systems' data for cross-referencing.
    """
    try:
        # Calculate astrology
        astro_data = calculate_natal_chart(
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

        # Calculate Human Design
        from ..services.geolocation import get_latitude_longitude

        # Use place for geocoding if provided, otherwise use lat/lng directly
        if hasattr(request, 'place') and request.place:
            coords = get_latitude_longitude(request.place)
            lat, lng = coords[0], coords[1]
        else:
            lat, lng = request.lat, request.lng

        hd_data = hd.get_bodygraph(
            name=request.name,
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            lat=lat,
            lng=lng,
            tz_str=request.tz_str
        )

        return {
            "name": request.name,
            "birth_data": {
                "date": f"{request.year}-{request.month:02d}-{request.day:02d}",
                "time": f"{request.hour:02d}:{request.minute:02d}",
                "location": {
                    "lat": request.lat,
                    "lng": request.lng,
                    "timezone": request.tz_str
                }
            },
            "astrology": astro_data,
            "human_design": hd_data,
            "synthesis_notes": {
                "sun_sign": astro_data.get("sun", {}).get("sign"),
                "hd_type": hd_data.get("type"),
                "cross_system_resonance": "Available in future versions"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/charts")
async def generate_both_charts(request: SynthesisRequest):
    """
    Generate both natal chart (astrology) and bodygraph (HD) visualizations.

    Returns:
    - Base64-encoded astrology chart (PNG)
    - Base64-encoded bodygraph (SVG)
    """
    try:
        from ..services.astro_renderer import render_natal_chart
        from ..services.hd_renderer import render_bodygraph
        import base64

        # Generate astrology chart
        astro_chart, _ = render_natal_chart(
            name=request.name,
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            lat=request.lat,
            lng=request.lng,
            tz_str=request.tz_str,
            output_format="png",
            house_system=request.house_system
        )

        # Generate HD bodygraph
        from ..services.chart_renderer import generate_chart_svg
        from ..services.geolocation import get_latitude_longitude

        if hasattr(request, 'place') and request.place:
            coords = get_latitude_longitude(request.place)
            lat, lng = coords[0], coords[1]
        else:
            lat, lng = request.lat, request.lng

        hd_chart_data = hd.get_bodygraph(
            name=request.name,
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            lat=lat,
            lng=lng,
            tz_str=request.tz_str
        )
        bodygraph_svg = generate_chart_svg(hd_chart_data)

        return {
            "astrology_chart": {
                "format": "png",
                "data": base64.b64encode(astro_chart).decode('utf-8')
            },
            "bodygraph": {
                "format": "svg",
                "data": base64.b64encode(bodygraph_svg.encode('utf-8')).decode('utf-8')
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
