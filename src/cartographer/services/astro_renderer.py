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
    house_system: str = "P"
):
    """
    Render natal chart visualization using Kerykeion.

    Args:
        output_format: "png", "svg", or "pdf"

    Returns:
        Tuple of (image_bytes, media_type)
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
        city="",
        nation="",
        zodiac_type="Tropic",
        online=False
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
