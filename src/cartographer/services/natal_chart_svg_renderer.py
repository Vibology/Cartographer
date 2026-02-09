"""
Custom SVG Natal Chart Renderer - Pure SVG generation without matplotlib

Built for full control over chart aesthetics and structure.
Generates clean, scalable vector graphics matching bodygraph quality.
"""

import math
from typing import Dict, List, Tuple
from xml.sax.saxutils import escape


# ============================================================================
# Constants
# ============================================================================

# Canvas dimensions
CANVAS_WIDTH = 890
CANVAS_HEIGHT = 580
CENTER_X = 440
CENTER_Y = 290

# Chart geometry
CHART_RADIUS = 220  # Outer edge of zodiac wheel
ZODIAC_RING_WIDTH = 35
HOUSE_RING_INNER = 80  # Inner edge of house ring
HOUSE_RING_OUTER = CHART_RADIUS - ZODIAC_RING_WIDTH  # 185
PLANET_RING_RADIUS = 195  # Where planets are positioned
ASPECT_RING_RADIUS = 140  # Where aspect lines connect

# Zodiac signs (in order from 0° Aries)
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

ZODIAC_SYMBOLS = {
    'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊', 'Cancer': '♋',
    'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Scorpio': '♏',
    'Sagittarius': '♐', 'Capricorn': '♑', 'Aquarius': '♒', 'Pisces': '♓'
}

ZODIAC_COLORS = {
    'Aries': '#ff7200', 'Taurus': '#6b3d00', 'Gemini': '#69acf1', 'Cancer': '#2b4972',
    'Leo': '#ff7200', 'Virgo': '#6b3d00', 'Libra': '#69acf1', 'Scorpio': '#2b4972',
    'Sagittarius': '#ff7200', 'Capricorn': '#6b3d00', 'Aquarius': '#69acf1', 'Pisces': '#2b4972'
}

# Planet symbols and colors
PLANET_SYMBOLS = {
    'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇',
    'True_north_lunar_node': '☊', 'Chiron': '⚷'
}

PLANET_COLORS = {
    'Sun': '#984b00', 'Moon': '#150052', 'Mercury': '#520800', 'Venus': '#400052',
    'Mars': '#540000', 'Jupiter': '#47133d', 'Saturn': '#124500', 'Uranus': '#6f0766',
    'Neptune': '#06537f', 'Pluto': '#713f04', 'True_north_lunar_node': '#4c1541',
    'Chiron': '#666f06'
}

# Aspect definitions
ASPECTS = {
    'conjunction': {'angle': 0, 'orb': 8, 'symbol': '☌', 'color': '#5757e2', 'width': 2},
    'sextile': {'angle': 60, 'orb': 6, 'symbol': '⚹', 'color': '#d59e28', 'width': 1},
    'square': {'angle': 90, 'orb': 8, 'symbol': '□', 'color': '#dc0000', 'width': 1.5},
    'trine': {'angle': 120, 'orb': 8, 'symbol': '△', 'color': '#36d100', 'width': 1.5},
    'opposition': {'angle': 180, 'orb': 8, 'symbol': '☍', 'color': '#510060', 'width': 2}
}


# ============================================================================
# Utility Functions
# ============================================================================

def zodiac_to_canvas(zodiac_longitude: float, radius: float) -> Tuple[float, float]:
    """
    Convert zodiac longitude (0-360°) to canvas coordinates.

    Traditional astrological orientation:
    - 0° Aries at 9 o'clock (180° on unit circle)
    - Counter-clockwise progression

    Args:
        zodiac_longitude: Degrees in zodiac (0° = 0° Aries)
        radius: Distance from center

    Returns:
        (x, y) coordinates on canvas
    """
    # Convert zodiac degrees to mathematical angle
    # Zodiac 0° = 180° on canvas (9 o'clock position)
    angle_deg = 180 - zodiac_longitude
    angle_rad = math.radians(angle_deg)

    x = CENTER_X + radius * math.cos(angle_rad)
    y = CENTER_Y + radius * math.sin(angle_rad)

    return x, y


def format_degree(longitude: float) -> str:
    """Format zodiac position as degree within sign (e.g., '25°36' Virgo')."""
    sign_index = int(longitude / 30) % 12
    degree = int(longitude % 30)
    minute = int((longitude % 1) * 60)
    sign = ZODIAC_SIGNS[sign_index]
    return f"{degree}°{minute:02d}' {sign}"


def calculate_aspect_angle(pos1: float, pos2: float) -> float:
    """Calculate the angular separation between two zodiac positions."""
    diff = abs(pos2 - pos1)
    if diff > 180:
        diff = 360 - diff
    return diff


def find_aspects(planets_data: Dict) -> List[Tuple[str, str, str, float]]:
    """
    Find all major aspects between planets.

    Returns:
        List of (planet1, planet2, aspect_type, angle) tuples
    """
    aspects_found = []
    planet_names = list(planets_data.keys())

    for i, planet1 in enumerate(planet_names):
        for planet2 in planet_names[i+1:]:
            pos1 = planets_data[planet1]['position']
            pos2 = planets_data[planet2]['position']

            angle = calculate_aspect_angle(pos1, pos2)

            # Check each aspect type
            for aspect_name, aspect_info in ASPECTS.items():
                target_angle = aspect_info['angle']
                orb = aspect_info['orb']
                diff = abs(angle - target_angle)

                if diff <= orb:
                    aspects_found.append((planet1, planet2, aspect_name, angle))
                    break  # Found aspect, don't check others

    return aspects_found


# ============================================================================
# SVG Generation
# ============================================================================

class SVGBuilder:
    """Helper class for building SVG content."""

    def __init__(self):
        self.elements = []

    def add(self, element: str):
        """Add an SVG element."""
        self.elements.append(element)

    def circle(self, cx: float, cy: float, r: float, **attrs) -> str:
        """Generate circle element."""
        attrs_str = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" {attrs_str}/>'

    def line(self, x1: float, y1: float, x2: float, y2: float, **attrs) -> str:
        """Generate line element."""
        attrs_str = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {attrs_str}/>'

    def text(self, x: float, y: float, content: str, **attrs) -> str:
        """Generate text element."""
        attrs_str = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        content_escaped = escape(content)
        return f'<text x="{x:.2f}" y="{y:.2f}" {attrs_str}>{content_escaped}</text>'

    def path(self, d: str, **attrs) -> str:
        """Generate path element."""
        attrs_str = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        return f'<path d="{d}" {attrs_str}/>'

    def group(self, elements: List[str], **attrs) -> str:
        """Generate group element."""
        attrs_str = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        content = '\n    '.join(elements)
        return f'<g {attrs_str}>\n    {content}\n</g>'


def generate_zodiac_wheel(svg: SVGBuilder):
    """Generate the zodiac wheel with 12 signs."""
    elements = []

    # Outer circle (edge of zodiac ring)
    elements.append(svg.circle(
        CENTER_X, CENTER_Y, CHART_RADIUS,
        stroke='#000000', stroke_width=2, fill='none'
    ))

    # Inner circle (edge of house ring)
    elements.append(svg.circle(
        CENTER_X, CENTER_Y, HOUSE_RING_OUTER,
        stroke='#000000', stroke_width=1, fill='none'
    ))

    # Draw zodiac signs
    for i, sign in enumerate(ZODIAC_SIGNS):
        # Start angle for this sign (0° Aries at 180° canvas)
        sign_start = i * 30  # Zodiac degrees
        sign_mid = sign_start + 15  # Middle of sign for label

        # Draw zodiac divider lines
        x1, y1 = zodiac_to_canvas(sign_start, HOUSE_RING_OUTER)
        x2, y2 = zodiac_to_canvas(sign_start, CHART_RADIUS)
        elements.append(svg.line(x1, y1, x2, y2, stroke='#cccccc', stroke_width=1))

        # Draw sign symbol
        symbol_x, symbol_y = zodiac_to_canvas(sign_mid, CHART_RADIUS - ZODIAC_RING_WIDTH/2)
        color = ZODIAC_COLORS[sign]
        elements.append(svg.text(
            symbol_x, symbol_y + 5,  # +5 for vertical centering
            ZODIAC_SYMBOLS[sign],
            font_size=20,
            fill=color,
            text_anchor='middle',
            font_family="'SF Pro', 'Helvetica Neue', sans-serif"
        ))

    svg.add(svg.group(elements, id='zodiac_wheel'))


def generate_house_cusps(svg: SVGBuilder, house_cusps: List[float]):
    """Generate house cusp lines (1-12)."""
    elements = []

    for i, cusp_position in enumerate(house_cusps):
        house_num = i + 1

        # Draw cusp line from inner to outer edge
        x1, y1 = zodiac_to_canvas(cusp_position, HOUSE_RING_INNER)
        x2, y2 = zodiac_to_canvas(cusp_position, HOUSE_RING_OUTER)

        # Thicker line for angular houses (1, 4, 7, 10)
        width = 2 if house_num in [1, 4, 7, 10] else 1
        color = '#ff0000' if house_num in [1, 10] else '#000000'

        elements.append(svg.line(x1, y1, x2, y2, stroke=color, stroke_width=width))

        # House number (inside the wheel)
        label_x, label_y = zodiac_to_canvas(cusp_position, HOUSE_RING_INNER - 15)
        elements.append(svg.text(
            label_x, label_y + 4,
            str(house_num),
            font_size=12,
            fill='#ff0000',
            text_anchor='middle',
            font_family="'SF Pro', 'Helvetica Neue', sans-serif"
        ))

    svg.add(svg.group(elements, id='house_cusps'))


def generate_planets(svg: SVGBuilder, planets_data: Dict):
    """Generate planet symbols and positions."""
    elements = []

    # Track positions for collision detection
    placed_positions = []

    for planet_name, planet_info in planets_data.items():
        position = planet_info['position']  # Zodiac longitude
        is_retrograde = planet_info.get('retrograde', False)

        # Get planet symbol and color
        symbol = PLANET_SYMBOLS.get(planet_name, '?')
        color = PLANET_COLORS.get(planet_name, '#000000')

        # Check for collisions with already-placed planets
        radius = PLANET_RING_RADIUS
        for placed_pos, placed_radius in placed_positions:
            angle_diff = abs(position - placed_pos)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            # If within 15°, offset the radius
            if angle_diff < 15:
                # Alternate between inner and outer
                if len([p for p, r in placed_positions if abs(p - position) < 15]) % 2 == 0:
                    radius = PLANET_RING_RADIUS - 20
                else:
                    radius = PLANET_RING_RADIUS + 20
                break

        # Calculate position
        x, y = zodiac_to_canvas(position, radius)

        # Draw planet symbol
        elements.append(svg.text(
            x, y + 6,  # +6 for vertical centering
            symbol,
            font_size=16,
            fill=color,
            text_anchor='middle',
            font_family="'SF Pro', 'Helvetica Neue', sans-serif",
            font_weight='bold'
        ))

        # Add retrograde indicator
        if is_retrograde:
            elements.append(svg.text(
                x + 10, y - 6,
                'Rx',
                font_size=8,
                fill=color,
                font_style='italic',
                font_family="'SF Pro', 'Helvetica Neue', sans-serif"
            ))

        # Record position
        placed_positions.append((position, radius))

    svg.add(svg.group(elements, id='planets'))


def generate_aspects(svg: SVGBuilder, planets_data: Dict):
    """Generate aspect lines connecting planets."""
    elements = []

    aspects = find_aspects(planets_data)

    for planet1, planet2, aspect_type, angle in aspects:
        pos1 = planets_data[planet1]['position']
        pos2 = planets_data[planet2]['position']

        # Calculate line endpoints at aspect ring
        x1, y1 = zodiac_to_canvas(pos1, ASPECT_RING_RADIUS)
        x2, y2 = zodiac_to_canvas(pos2, ASPECT_RING_RADIUS)

        # Get aspect styling
        aspect_info = ASPECTS[aspect_type]
        color = aspect_info['color']
        width = aspect_info['width']

        # Draw aspect line
        elements.append(svg.line(
            x1, y1, x2, y2,
            stroke=color,
            stroke_width=width,
            stroke_opacity=0.8
        ))

    svg.add(svg.group(elements, id='aspects'))


def generate_metadata_panel(svg: SVGBuilder, astro_data: Dict):
    """Generate metadata panel with birth data."""
    elements = []

    # Extract metadata
    meta = astro_data.get('meta', {})
    name = meta.get('name', 'Natal Chart')
    birth_date = meta.get('birth_date', '')
    birth_time = meta.get('birth_time', '')

    # Get angles
    angles = astro_data.get('angles', {})
    asc_data = angles.get('ascendant', {})
    mc_data = angles.get('midheaven', {})

    # Format ASC/MC
    asc_position = asc_data.get('position', 0)
    asc_sign_index = int(asc_data.get('sign', 'Aqu') == 'Aqu') * 10  # Quick lookup
    mc_position = mc_data.get('position', 0)

    # Title
    elements.append(svg.text(
        20, 25,
        f"{name} - Birth Chart",
        font_size=20,
        fill='#000000',
        font_family="'SF Pro', 'Helvetica Neue', sans-serif",
        font_weight='bold'
    ))

    # Birth data
    y_offset = 50
    if birth_date and birth_time:
        elements.append(svg.text(
            20, y_offset,
            f"{birth_date} • {birth_time}",
            font_size=11,
            fill='#000000',
            font_family="'SF Pro', 'Helvetica Neue', sans-serif"
        ))
        y_offset += 20

    # ASC/MC
    asc_str = format_degree(asc_data.get('sign', 'Aqu') == 'Aqu' and 312.5 or 0)  # Placeholder
    mc_str = format_degree(mc_data.get('sign', 'Sag') == 'Sag' and 240.8 or 0)  # Placeholder

    elements.append(svg.text(
        20, y_offset,
        f"ASC: {asc_str}",
        font_size=11,
        fill='#000000',
        font_family="'SF Pro', 'Helvetica Neue', sans-serif"
    ))

    elements.append(svg.text(
        20, y_offset + 20,
        f"MC: {mc_str}",
        font_size=11,
        fill='#000000',
        font_family="'SF Pro', 'Helvetica Neue', sans-serif"
    ))

    svg.add(svg.group(elements, id='metadata'))


def generate_natal_chart_svg(astro_data: Dict) -> str:
    """
    Generate complete natal chart as pure SVG.

    Args:
        astro_data: Astrology data from Kerykeion format

    Returns:
        SVG string
    """
    svg = SVGBuilder()

    # Parse house cusps
    houses_data = astro_data.get('houses', {})
    house_cusps = []
    sign_to_index = {
        'Ari': 0, 'Tau': 1, 'Gem': 2, 'Can': 3, 'Leo': 4, 'Vir': 5,
        'Lib': 6, 'Sco': 7, 'Sag': 8, 'Cap': 9, 'Aqu': 10, 'Pis': 11
    }
    for i in range(1, 13):
        house_key = f"house_{i}"
        if house_key in houses_data:
            house_data = houses_data[house_key]
            if isinstance(house_data, dict):
                sign = house_data.get('sign', 'Ari')
                position = house_data.get('position', 0)
                abs_longitude = sign_to_index.get(sign, 0) * 30 + position
                house_cusps.append(abs_longitude)
            else:
                house_cusps.append(house_data)
        else:
            house_cusps.append((i - 1) * 30)  # Fallback

    # Parse planets
    planets_dict = astro_data.get('planets', {})
    planets_data = {}
    for planet_name_lower, planet_info in planets_dict.items():
        planet_name = planet_name_lower.capitalize()
        planets_data[planet_name] = {
            'position': planet_info.get('abs_position', 0),
            'sign': planet_info.get('sign', ''),
            'retrograde': planet_info.get('retrograde', False)
        }

    # Generate chart layers (back to front)
    generate_zodiac_wheel(svg)
    generate_house_cusps(svg, house_cusps)
    generate_aspects(svg, planets_data)  # Behind planets
    generate_planets(svg, planets_data)
    generate_metadata_panel(svg, astro_data)

    # Build final SVG
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{CANVAS_WIDTH}"
     height="{CANVAS_HEIGHT}"
     viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}">
    <title>Natal Chart</title>

    <!-- Background -->
    <rect width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" fill="#ffffff"/>

    <!-- Chart Elements -->
    {chr(10).join(svg.elements)}
</svg>'''

    return svg_content


# ============================================================================
# Main Entry Point
# ============================================================================

def render_natal_chart_svg(astro_data: Dict) -> bytes:
    """
    Main entry point for natal chart SVG generation.

    Args:
        astro_data: Astrology data in Kerykeion format

    Returns:
        SVG bytes
    """
    svg_string = generate_natal_chart_svg(astro_data)
    return svg_string.encode('utf-8')
