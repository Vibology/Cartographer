"""
Astrology Chart Rendering Service - Kerykeion chart generation
"""

from kerykeion import AstrologicalSubject, KerykeionChartSVG
import io
import re


# Square chart dimensions for panel-friendly viewing
# Results in ~700×730 viewBox (aspect ratio ~0.96:1, effectively square)
SQUARE_CHART_WIDTH = 700
SQUARE_CHART_HEIGHT = 700


def _inject_font_family(svg_content: str) -> str:
    """Inject SF Pro font-family and spacing fixes into Kerykeion SVG output.

    Adds CSS rules to:
    1. Use SF Pro font (with system fallbacks)
    2. Reduce font size and letter-spacing to prevent column overlap
    """
    font_rule = (
        "text { "
        "font-family: 'SF Pro', 'SF Pro Display', '-apple-system', 'Helvetica Neue', sans-serif; "
        "font-size: 9px; "  # Smaller font to prevent column overlap
        "letter-spacing: -0.5px; "  # Tighter kerning for degree/minute/second symbols
        "}\n"
    )
    # Insert after opening <style> tag
    if "<style" in svg_content:
        svg_content = re.sub(
            r'(<style[^>]*>)',
            r'\1\n        ' + font_rule + '        ',
            svg_content,
            count=1
        )
    else:
        # No style tag — inject one after the opening <svg> tag
        svg_content = svg_content.replace(
            '<title>',
            f'<style>{font_rule}</style>\n    <title>',
            1
        )
    return svg_content

def _fix_cusp_alignment(svg_content: str) -> str:
    """Fix cusp label alignment to be left-justified.

    Kerykeion generates right-aligned cusp labels with non-breaking space padding,
    causing inconsistent spacing. This converts them to left-aligned text.
    """
    # Remove non-breaking spaces before cusp numbers and change to left alignment
    # Pattern: <text text-anchor='end' x='40' ...>Cusp &#160;&#160;1:</text>
    # Replace with: <text x='0' ...>Cusp 1:</text>
    svg_content = re.sub(
        r"<text text-anchor='end' x='40'([^>]*)>Cusp\s*(?:&#160;)*(\d+):",
        r"<text x='0'\1>Cusp \2:",
        svg_content
    )
    return svg_content

def _adjust_planet_grid_spacing(svg_content: str) -> str:
    """Increase spacing between planet positions and zodiac sign symbols.

    Moves zodiac symbols and retrograde indicators further right to prevent overlap
    with degree/minute/second text in the planetary positions grid.
    """
    # Move zodiac sign symbols from translate(60,-8) to translate(75,-8)
    svg_content = re.sub(
        r"<g transform='translate\(60,-8\)'><use transform='scale\(0\.3\)' xlink:href='#(Ari|Tau|Gem|Can|Leo|Vir|Lib|Sco|Sag|Cap|Aqu|Pis)' /></g>",
        r"<g transform='translate(75,-8)'><use transform='scale(0.3)' xlink:href='#\1' /></g>",
        svg_content
    )

    # Move retrograde symbols from translate(74,-6) to translate(89,-6)
    svg_content = re.sub(
        r"<g transform='translate\(74,-6\)'><use transform='scale\(\.5\)' xlink:href='#retrograde' /></g>",
        r"<g transform='translate(89,-6)'><use transform='scale(.5)' xlink:href='#retrograde' /></g>",
        svg_content
    )

    return svg_content

def _combine_location_line(svg_content: str) -> str:
    """Combine 'Location:' label and city name onto a single line.

    Kerykeion generates these as separate text elements on different lines.
    This merges them and adjusts subsequent line positions.
    """
    # Find Location: and city text elements
    location_pattern = (
        r"(<text kr:node='Top_Left_Text_0'[^>]*y='58'[^>]*>Location:</text>)\s*"
        r"<text kr:node='Top_Left_Text_1'[^>]*y='70'[^>]*>([^<]+)</text>"
    )

    # Replace with combined single-line text
    svg_content = re.sub(
        location_pattern,
        r"<text kr:node='Top_Left_Text_0' x='20' y='58' style='fill: var(--kerykeion-chart-color-paper-0); font-size: 10px'>Location: \2</text>",
        svg_content
    )

    # Shift subsequent text elements up by 12 pixels (the removed line spacing)
    # Top_Left_Text_2: y='82' -> y='70'
    svg_content = re.sub(
        r"(<text kr:node='Top_Left_Text_2'[^>]*)y='82'",
        r"\1y='70'",
        svg_content
    )
    # Top_Left_Text_3: y='94' -> y='82'
    svg_content = re.sub(
        r"(<text kr:node='Top_Left_Text_3'[^>]*)y='94'",
        r"\1y='82'",
        svg_content
    )
    # Top_Left_Text_4: y='106' -> y='94'
    svg_content = re.sub(
        r"(<text kr:node='Top_Left_Text_4'[^>]*)y='106'",
        r"\1y='94'",
        svg_content
    )
    # Top_Left_Text_5: y='118' -> y='106'
    svg_content = re.sub(
        r"(<text kr:node='Top_Left_Text_5'[^>]*)y='118'",
        r"\1y='106'",
        svg_content
    )

    return svg_content

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

    # Generate SVG chart with square dimensions (700×700 → ~700×730 viewBox)
    chart = KerykeionChartSVG(subject, chart_type="Natal")

    # Initialize internal chart drawer and set square dimensions
    chart._ensure_chart()
    chart._chart_drawer.width = SQUARE_CHART_WIDTH
    chart._chart_drawer.height = SQUARE_CHART_HEIGHT

    svg_content = chart.makeTemplate()

    # Inject SF Pro font-family into SVG (Kerykeion templates have no explicit font)
    svg_content = _inject_font_family(svg_content)

    # Fix cusp alignment to be left-justified
    svg_content = _fix_cusp_alignment(svg_content)

    # Adjust planet grid spacing to prevent overlap
    svg_content = _adjust_planet_grid_spacing(svg_content)

    # Combine location label and city name onto single line
    svg_content = _combine_location_line(svg_content)

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
