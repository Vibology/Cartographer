"""
Astrology Chart Rendering Service - Kerykeion chart generation
"""

from kerykeion import AstrologicalSubject, KerykeionChartSVG
import io

def render_natal_chart(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lng: float,
    tz_str: str,
    output_format: str = "png",
    house_system: str = "P",
    city: str = None
):
    """
    Render natal chart visualization using Kerykeion.

    Args:
        output_format: "png", "svg", or "pdf"
        city: Optional city name (will attempt reverse geocode if not provided)

    Returns:
        Tuple of (image_bytes, media_type)
    """
    # Get city name and nation if not provided
    nation = "US"  # Default to US
    if not city:
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="cartographer")
            location = geolocator.reverse(f"{lat}, {lng}", language='en')
            if location:
                # Extract location components
                address = location.raw.get('address', {})
                city_name = address.get('city') or address.get('town') or address.get('village')
                state_code = address.get('ISO3166-2-lvl4', '').split('-')[-1] if 'ISO3166-2-lvl4' in address else address.get('state')
                country_code = address.get('country_code', '').upper()

                # Set nation from geocoding
                nation = country_code if country_code else "US"

                # Build location string (City, State for US; City, Country otherwise)
                if country_code == 'US' and city_name and state_code:
                    city = f"{city_name}, {state_code}"
                elif city_name:
                    country = address.get('country', '')
                    city = f"{city_name}, {country}" if country else city_name
                else:
                    city = f"{lat:.4f}, {lng:.4f}"
            else:
                city = f"{lat:.4f}, {lng:.4f}"
        except:
            city = f"{lat:.4f}, {lng:.4f}"

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
        city=city,
        nation=nation
    )

    # Generate SVG chart
    chart = KerykeionChartSVG(subject, chart_type="Natal")
    svg_content = chart.makeTemplate()

    if output_format == "svg":
        return svg_content.encode('utf-8'), "image/svg+xml"

    elif output_format == "png":
        # Convert SVG to PNG using cairosvg
        try:
            import cairosvg
            png_bytes = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
            return png_bytes, "image/png"
        except ImportError:
            # Fallback: return SVG if cairosvg not available
            return svg_content.encode('utf-8'), "image/svg+xml"

    elif output_format == "pdf":
        # Convert SVG to PDF
        try:
            import cairosvg
            pdf_bytes = cairosvg.svg2pdf(bytestring=svg_content.encode('utf-8'))
            return pdf_bytes, "application/pdf"
        except ImportError:
            # Fallback: return SVG
            return svg_content.encode('utf-8'), "image/svg+xml"

    else:
        # Default to SVG
        return svg_content.encode('utf-8'), "image/svg+xml"
