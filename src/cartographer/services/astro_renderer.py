"""
Astrology Chart Rendering Service - Kerykeion chart generation
"""

from kerykeion import AstrologicalSubject, KerykeionChartSVG
import io
import re


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


def _fix_viewbox_clipping(svg_content: str) -> str:
    """Expand viewBox to prevent degree marker clipping.

    Kerykeion's default viewBox='0 -15 890 580' clips rotated degree labels.
    Expand to give more breathing room.
    """
    # Expand viewBox: add padding on all sides
    svg_content = re.sub(
        r"viewBox='0 -15 890 580'",
        r"viewBox='-30 -45 950 650'",
        svg_content
    )

    return svg_content


def _enhance_colors(svg_content: str) -> str:
    """Enhance color palette for better visual identity.

    Makes zodiac wheel more vibrant and aspects more visible.
    """
    # More vibrant zodiac colors (Fire=red/orange, Earth=green/brown, Air=blue/purple, Water=blue/teal)
    color_replacements = {
        # Fire signs (Aries, Leo, Sag) - vibrant reds/oranges
        '--kerykeion-chart-color-zodiac-bg-0': '#ff4500',  # Aries - red-orange
        '--kerykeion-chart-color-zodiac-bg-4': '#ff6b35',  # Leo - coral
        '--kerykeion-chart-color-zodiac-bg-8': '#ff8c42',  # Sag - light orange

        # Earth signs (Taurus, Virgo, Cap) - greens/browns
        '--kerykeion-chart-color-zodiac-bg-1': '#6b8e23',  # Taurus - olive green
        '--kerykeion-chart-color-zodiac-bg-5': '#8b7355',  # Virgo - earth brown
        '--kerykeion-chart-color-zodiac-bg-9': '#556b2f',  # Cap - dark olive

        # Air signs (Gemini, Libra, Aquarius) - blues/purples
        '--kerykeion-chart-color-zodiac-bg-2': '#4682b4',  # Gemini - steel blue
        '--kerykeion-chart-color-zodiac-bg-6': '#6a5acd',  # Libra - slate blue
        '--kerykeion-chart-color-zodiac-bg-10': '#5f9ea0', # Aquarius - cadet blue

        # Water signs (Cancer, Scorpio, Pisces) - deep blues/teals
        '--kerykeion-chart-color-zodiac-bg-3': '#20b2aa',  # Cancer - light sea green
        '--kerykeion-chart-color-zodiac-bg-7': '#483d8b',  # Scorpio - dark slate blue
        '--kerykeion-chart-color-zodiac-bg-11': '#4169e1', # Pisces - royal blue
    }

    for var_name, color in color_replacements.items():
        svg_content = re.sub(
            rf'{var_name}: #[0-9a-fA-F]{{6}};',
            f'{var_name}: {color};',
            svg_content
        )

    # Make aspect colors more vibrant and visible
    aspect_color_replacements = {
        '--kerykeion-chart-color-conjunction': '#5555ff',  # Bright blue
        '--kerykeion-chart-color-sextile': '#ffa500',      # Orange
        '--kerykeion-chart-color-square': '#ff0000',       # Pure red
        '--kerykeion-chart-color-trine': '#00ff00',        # Bright green
        '--kerykeion-chart-color-opposition': '#9932cc',   # Dark orchid
    }

    for var_name, color in aspect_color_replacements.items():
        svg_content = re.sub(
            rf'{var_name}: #[0-9a-fA-F]{{6}};',
            f'{var_name}: {color};',
            svg_content
        )

    return svg_content


def _improve_typography(svg_content: str) -> str:
    """Improve typography and text rendering.

    Better font sizes, weights, and spacing for improved readability.
    """
    # Increase title font size for better hierarchy
    svg_content = re.sub(
        r"(kr:node='Chart_Title'[^>]*style='[^']*font-size:)\s*24px",
        r"\1 28px; font-weight: 600",
        svg_content
    )

    # Make planet symbols slightly larger
    svg_content = re.sub(
        r"(xlink:href='#(Sun|Moon|Mercury|Venus|Mars|Jupiter|Saturn|Uranus|Neptune|Pluto)'[^/]*/?>)",
        lambda m: m.group(1).replace("scale(0.4)", "scale(0.45)") if "scale(0.4)" in m.group(1) else m.group(1),
        svg_content
    )

    return svg_content


def _build_portrait_chart(svg_content: str) -> str:
    """Build portrait chart with only essential elements using regex extraction.

    Phase 1: Extract and position only:
    1. Title (centered at x=310)
    2. Zodiacal information (upper left at 20,35)
    3. Location metadata (upper right at 330,35)
    4. Moon phase graphic (left at 20,135)
    5. Wheel (centered at 70,140)
    """
    # Extract style section
    style_match = re.search(r'(<style[^>]*>.*?</style>)', svg_content, re.DOTALL)
    style_section = style_match.group(1) if style_match else ''

    # Extract defs section (contains planet/zodiac symbols)
    defs_match = re.search(r'(<defs[^>]*>.*?</defs>)', svg_content, re.DOTALL)
    defs_section = defs_match.group(1) if defs_match else ''

    # 1. Extract title text
    title_match = re.search(r"<text[^>]*kr:node='Chart_Title'[^>]*>([^<]+)</text>", svg_content)
    title_text = title_match.group(1) if title_match else 'Birth Chart'

    # 2. Extract zodiacal information group (Bottom_Left_Text)
    zodiac_match = re.search(
        r"<g kr:node='Bottom_Left_Text'[^>]*>(.*?)</g>",
        svg_content,
        re.DOTALL
    )
    zodiac_content = zodiac_match.group(1) if zodiac_match else ''

    # 3. Extract location metadata group (Top_Left_Text)
    location_match = re.search(
        r"<g kr:node='Top_Left_Text'[^>]*>(.*?)</g>",
        svg_content,
        re.DOTALL
    )
    location_content = location_match.group(1) if location_match else ''

    # 4. Extract moon phase graphic (Lunar_Phase)
    moon_match = re.search(
        r"<g kr:node='Lunar_Phase'[^>]*>(.*?)</g>",
        svg_content,
        re.DOTALL
    )
    moon_content = moon_match.group(1) if moon_match else ''

    # 5. Extract wheel (Full_Wheel) - this is complex, need to get all nested content
    wheel_match = re.search(
        r"<g kr:node='Full_Wheel'[^>]*>(.*?)</g>\s*<g kr:node='Houses_And_Planets_Grid'",
        svg_content,
        re.DOTALL
    )
    wheel_content = wheel_match.group(1) if wheel_match else ''

    # Build new portrait SVG
    portrait_svg = f"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:kr='https://www.kerykeion.net/'
     width='620' height='920' viewBox='0 0 620 920'>
    <title>Natal Chart - Portrait</title>

    {style_section}
    {defs_section}

    <!-- Title (centered) -->
    <text kr:node='Chart_Title' x='310' y='22' text-anchor='middle' style='fill: var(--kerykeion-chart-color-paper-0); font-size: 28px; font-weight: 600'>{title_text}</text>

    <!-- Zodiacal Information (upper left) -->
    <g kr:node='Bottom_Left_Text' transform='translate(20,35)'>
{zodiac_content}    </g>

    <!-- Location Metadata (upper right) -->
    <g kr:node='Top_Left_Text' transform='translate(330,35)'>
{location_content}    </g>

    <!-- Moon Phase Graphic (left side) -->
    <g kr:node='Lunar_Phase' transform='translate(20,135)'>
{moon_content}    </g>

    <!-- Wheel (centered) -->
    <g kr:node='Full_Wheel' transform='translate(70,140)'>
{wheel_content}    </g>

</svg>"""

    return portrait_svg

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

    # Apply visual enhancements (landscape format)
    svg_content = _fix_viewbox_clipping(svg_content)      # Fix degree marker clipping
    svg_content = _enhance_colors(svg_content)             # Vibrant color palette
    svg_content = _inject_font_family(svg_content)         # SF Pro typography
    svg_content = _improve_typography(svg_content)         # Better font sizes/weights
    svg_content = _fix_cusp_alignment(svg_content)         # Left-justify cusps
    svg_content = _adjust_planet_grid_spacing(svg_content) # Prevent overlap
    svg_content = _combine_location_line(svg_content)      # Single-line location
    # Note: Portrait conversion handled by portrait_builder.py in generate_chart_visuals.py

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


def render_minimal_natal_chart(
    name: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lng: float,
    tz_str: str,
    house_system: str = "P",
    city: str = None
):
    """
    Render minimal natal chart with ONLY geometry (no text labels).

    Generates natal wheel showing:
    - Zodiac circle with house lines
    - Aspect lines
    - Planet glyphs at positions

    NO text overlays (degrees, house numbers, sign names, etc.)
    Pure geometric visualization for use with SwiftUI native data display.

    Returns:
        Tuple of (svg_bytes, media_type)
    """
    import xml.etree.ElementTree as ET

    # Generate full natal chart SVG
    svg_content, _ = render_natal_chart(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        lat=lat,
        lng=lng,
        tz_str=tz_str,
        output_format="svg",
        house_system=house_system,
        city=city
    )

    # Parse SVG and remove all text elements
    svg_string = svg_content.decode('utf-8') if isinstance(svg_content, bytes) else svg_content

    # Register Kerykeion namespace to preserve it during parsing
    namespaces = {
        'svg': 'http://www.w3.org/2000/svg',
        'xlink': 'http://www.w3.org/1999/xlink',
        'kr': 'http://kerykeion.net'
    }

    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix if prefix != 'svg' else '', uri)

    # Parse SVG
    root = ET.fromstring(svg_string.encode('utf-8'))

    # Remove all <text> elements (preserving geometry and glyphs)
    for text_elem in root.findall('.//{http://www.w3.org/2000/svg}text'):
        parent = root.find('.//{http://www.w3.org/2000/svg}text/..', namespaces)
        if parent is not None:
            parent.remove(text_elem)
        else:
            # Text element is at root level
            root.remove(text_elem)

    # Convert back to string
    minimal_svg = ET.tostring(root, encoding='unicode')

    return minimal_svg.encode('utf-8'), "image/svg+xml"
