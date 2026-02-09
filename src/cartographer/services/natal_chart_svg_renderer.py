"""
Custom SVG Natal Chart Renderer - Pure SVG with Kerykeion-level quality

Built for full control with improved design polish.
Generates clean, scalable vector graphics matching bodygraph aesthetic.
"""

import math
from typing import Dict, List, Tuple, Optional
from xml.sax.saxutils import escape
from datetime import datetime


# ============================================================================
# Constants - Layout & Geometry
# ============================================================================

# Canvas dimensions (landscape orientation like Kerykeion)
CANVAS_WIDTH = 890
CANVAS_HEIGHT = 580

# Chart positioning (chart is offset from left edge)
CHART_OFFSET_X = 100
CHART_OFFSET_Y = 50
CHART_CENTER_X = 240  # Relative to offset
CHART_CENTER_Y = 240
CHART_RADIUS = 220  # Outer edge of zodiac wheel

# Absolute chart center
CENTER_X = CHART_OFFSET_X + CHART_CENTER_X
CENTER_Y = CHART_OFFSET_Y + CHART_CENTER_Y

# Chart rings
ZODIAC_RING_WIDTH = 35
HOUSE_RING_INNER = 75
HOUSE_RING_OUTER = CHART_RADIUS - ZODIAC_RING_WIDTH  # 185
PLANET_RING_RADIUS = 195
ASPECT_RING_RADIUS = 140

# Zodiac signs
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

ZODIAC_ABBREV = {
    'Ari': 'Aries', 'Tau': 'Taurus', 'Gem': 'Gemini', 'Can': 'Cancer',
    'Leo': 'Leo', 'Vir': 'Virgo', 'Lib': 'Libra', 'Sco': 'Scorpio',
    'Sag': 'Sagittarius', 'Cap': 'Capricorn', 'Aqu': 'Aquarius', 'Pis': 'Pisces'
}

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

# Planets
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

PLANET_NAMES = {
    'Sun': 'Sun', 'Moon': 'Moon', 'Mercury': 'Mercury', 'Venus': 'Venus',
    'Mars': 'Mars', 'Jupiter': 'Jupiter', 'Saturn': 'Saturn', 'Uranus': 'Uranus',
    'Neptune': 'Neptune', 'Pluto': 'Pluto', 'True_north_lunar_node': 'N. Node (T)',
    'Chiron': 'Chiron'
}

# Aspects
ASPECTS = {
    'conjunction': {'angle': 0, 'orb': 8, 'symbol': '☌', 'color': '#5757e2', 'width': 1},
    'sextile': {'angle': 60, 'orb': 6, 'symbol': '⚹', 'color': '#d59e28', 'width': 1},
    'square': {'angle': 90, 'orb': 8, 'symbol': '□', 'color': '#dc0000', 'width': 1.5},
    'trine': {'angle': 120, 'orb': 8, 'symbol': '△', 'color': '#36d100', 'width': 1.5},
    'opposition': {'angle': 180, 'orb': 8, 'symbol': '☍', 'color': '#510060', 'width': 1}
}

# Typography
FONT_FAMILY = "'SF Pro', 'SF Pro Display', '-apple-system', 'Helvetica Neue', sans-serif"
FONT_SIZE_TITLE = 24
FONT_SIZE_BODY = 10
FONT_SIZE_PLANET = 16
FONT_SIZE_ZODIAC = 20
FONT_SIZE_DEGREE = 9


# ============================================================================
# Utility Functions
# ============================================================================

def zodiac_to_canvas(zodiac_longitude: float, radius: float) -> Tuple[float, float]:
    """
    Convert zodiac longitude to canvas coordinates.

    Traditional orientation: 0° Aries at 9 o'clock, counter-clockwise.
    """
    angle_deg = 180 - zodiac_longitude
    angle_rad = math.radians(angle_deg)

    x = CENTER_X + radius * math.cos(angle_rad)
    y = CENTER_Y + radius * math.sin(angle_rad)

    return x, y


def format_degree_full(longitude: float) -> str:
    """Format as degree°minute'second\" within sign."""
    sign_index = int(longitude / 30) % 12
    degree = int(longitude % 30)
    minute = int((longitude % 1) * 60)
    second = int(((longitude % 1) * 60 - minute) * 60)
    sign = ZODIAC_SIGNS[sign_index]

    return f"{degree}°{minute:02d}'{second:02d}\""


def format_degree_short(longitude: float) -> str:
    """Format as degree° (no minutes/seconds)."""
    degree = int(longitude % 30)
    return f"{degree}°"


def get_zodiac_sign_name(longitude: float) -> str:
    """Get sign name from longitude."""
    sign_index = int(longitude / 30) % 12
    return ZODIAC_SIGNS[sign_index]


def calculate_aspect_angle(pos1: float, pos2: float) -> float:
    """Calculate angular separation between two positions."""
    diff = abs(pos2 - pos1)
    if diff > 180:
        diff = 360 - diff
    return diff


def find_aspects(planets_data: Dict) -> List[Tuple[str, str, str, float]]:
    """Find all major aspects between planets."""
    aspects_found = []
    planet_names = list(planets_data.keys())

    for i, planet1 in enumerate(planet_names):
        for planet2 in planet_names[i+1:]:
            pos1 = planets_data[planet1]['position']
            pos2 = planets_data[planet2]['position']

            angle = calculate_aspect_angle(pos1, pos2)

            for aspect_name, aspect_info in ASPECTS.items():
                target_angle = aspect_info['angle']
                orb = aspect_info['orb']
                diff = abs(angle - target_angle)

                if diff <= orb:
                    aspects_found.append((planet1, planet2, aspect_name, angle))
                    break

    return aspects_found


# ============================================================================
# SVG Builder Class
# ============================================================================

class SVGBuilder:
    """Helper for building SVG content."""

    def __init__(self):
        self.defs = []
        self.elements = []

    def add_def(self, element: str):
        """Add to defs section."""
        self.defs.append(element)

    def add(self, element: str):
        """Add SVG element."""
        self.elements.append(element)

    def circle(self, cx: float, cy: float, r: float, **attrs) -> str:
        """Generate circle."""
        attrs_str = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" {attrs_str}/>'

    def line(self, x1: float, y1: float, x2: float, y2: float, **attrs) -> str:
        """Generate line."""
        attrs_str = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {attrs_str}/>'

    def text(self, x: float, y: float, content: str, **attrs) -> str:
        """Generate text."""
        attrs_str = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        content_escaped = escape(content)
        return f'<text x="{x:.2f}" y="{y:.2f}" {attrs_str}>{content_escaped}</text>'

    def path(self, d: str, **attrs) -> str:
        """Generate path."""
        attrs_str = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        return f'<path d="{d}" {attrs_str}/>'

    def group(self, elements: List[str], **attrs) -> str:
        """Generate group."""
        if not elements:
            return ""
        attrs_str = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        content = '\n        '.join(elements)
        return f'<g {attrs_str}>\n        {content}\n    </g>'


# ============================================================================
# Chart Generation Functions
# ============================================================================

def generate_zodiac_wheel(svg: SVGBuilder):
    """Generate zodiac wheel with 12 signs."""
    elements = []

    # Outer circle
    elements.append(svg.circle(
        CENTER_X, CENTER_Y, CHART_RADIUS,
        stroke='#000000', stroke_width=2, fill='none'
    ))

    # Inner circle (house ring boundary)
    elements.append(svg.circle(
        CENTER_X, CENTER_Y, HOUSE_RING_OUTER,
        stroke='#000000', stroke_width=1, fill='none'
    ))

    # Draw each zodiac sign
    for i, sign in enumerate(ZODIAC_SIGNS):
        sign_start = i * 30
        sign_mid = sign_start + 15

        # Divider line
        x1, y1 = zodiac_to_canvas(sign_start, HOUSE_RING_OUTER)
        x2, y2 = zodiac_to_canvas(sign_start, CHART_RADIUS)
        elements.append(svg.line(x1, y1, x2, y2, stroke='#cccccc', stroke_width=1))

        # Sign symbol
        symbol_x, symbol_y = zodiac_to_canvas(sign_mid, CHART_RADIUS - ZODIAC_RING_WIDTH/2)
        color = ZODIAC_COLORS[sign]
        elements.append(svg.text(
            symbol_x, symbol_y + 7,
            ZODIAC_SYMBOLS[sign],
            font_size=FONT_SIZE_ZODIAC,
            fill=color,
            text_anchor='middle',
            font_family=FONT_FAMILY,
            font_weight='bold'
        ))

    svg.add(svg.group(elements, id='zodiac_wheel'))


def generate_house_cusps(svg: SVGBuilder, house_cusps: List[float]):
    """Generate house cusp lines."""
    elements = []

    for i, cusp_position in enumerate(house_cusps):
        house_num = i + 1

        # Draw cusp line
        x1, y1 = zodiac_to_canvas(cusp_position, HOUSE_RING_INNER)
        x2, y2 = zodiac_to_canvas(cusp_position, HOUSE_RING_OUTER)

        # Angular houses (1, 4, 7, 10) get thicker lines and red color
        is_angular = house_num in [1, 4, 7, 10]
        width = 2.5 if is_angular else 1
        color = '#ff0000' if is_angular else '#000000'

        elements.append(svg.line(x1, y1, x2, y2, stroke=color, stroke_width=width))

        # House number (inside wheel)
        label_x, label_y = zodiac_to_canvas(cusp_position, HOUSE_RING_INNER - 20)
        elements.append(svg.text(
            label_x, label_y + 4,
            str(house_num),
            font_size=11,
            fill='#ff0000' if is_angular else '#666666',
            text_anchor='middle',
            font_family=FONT_FAMILY,
            font_weight='bold' if is_angular else 'normal'
        ))

    svg.add(svg.group(elements, id='house_cusps'))


def generate_planets(svg: SVGBuilder, planets_data: Dict):
    """Generate planet symbols with collision detection."""
    elements = []
    placed_positions = []

    for planet_name, planet_info in planets_data.items():
        position = planet_info['position']
        is_retrograde = planet_info.get('retrograde', False)

        symbol = PLANET_SYMBOLS.get(planet_name, '?')
        color = PLANET_COLORS.get(planet_name, '#000000')

        # Collision detection
        radius = PLANET_RING_RADIUS
        for placed_pos, placed_radius in placed_positions:
            angle_diff = abs(position - placed_pos)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            if angle_diff < 12:
                # Alternate inner/outer
                count = len([p for p, r in placed_positions if abs(p - position) < 12])
                radius = PLANET_RING_RADIUS + (20 if count % 2 else -20)
                break

        # Draw planet symbol
        x, y = zodiac_to_canvas(position, radius)
        elements.append(svg.text(
            x, y + 6,
            symbol,
            font_size=FONT_SIZE_PLANET,
            fill=color,
            text_anchor='middle',
            font_family=FONT_FAMILY,
            font_weight='bold'
        ))

        # Retrograde indicator
        if is_retrograde:
            elements.append(svg.text(
                x + 11, y - 6,
                'Rx',
                font_size=7,
                fill=color,
                font_style='italic',
                font_family=FONT_FAMILY,
                opacity=0.8
            ))

        # Degree label line (from planet to outer edge)
        label_x, label_y = zodiac_to_canvas(position, CHART_RADIUS + 8)
        elements.append(svg.line(
            x, y, label_x, label_y,
            stroke=color,
            stroke_width=0.8,
            stroke_opacity=0.6
        ))

        # Degree label
        degree_text = format_degree_short(position)
        angle_deg = 180 - position
        rotation = angle_deg

        elements.append(
            f'<text x="{label_x:.2f}" y="{label_y:.2f}" '
            f'transform="rotate({rotation:.1f} {label_x:.2f} {label_y:.2f})" '
            f'font-size="{FONT_SIZE_DEGREE}" '
            f'fill="{color}" '
            f'text-anchor="middle" '
            f'font-family="{FONT_FAMILY}">{degree_text}</text>'
        )

        placed_positions.append((position, radius))

    svg.add(svg.group(elements, id='planets'))


def generate_aspects(svg: SVGBuilder, planets_data: Dict):
    """Generate aspect lines."""
    elements = []
    aspects = find_aspects(planets_data)

    for planet1, planet2, aspect_type, angle in aspects:
        pos1 = planets_data[planet1]['position']
        pos2 = planets_data[planet2]['position']

        # Draw at aspect ring radius
        x1, y1 = zodiac_to_canvas(pos1, ASPECT_RING_RADIUS)
        x2, y2 = zodiac_to_canvas(pos2, ASPECT_RING_RADIUS)

        aspect_info = ASPECTS[aspect_type]
        # Generate line directly to control class attribute
        elements.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'class="aspect" '
            f'stroke="{aspect_info["color"]}" '
            f'stroke-width="{aspect_info["width"]}" '
            f'stroke-opacity="0.9"/>'
        )

    svg.add(svg.group(elements, id='aspects'))


def generate_metadata_panel(svg: SVGBuilder, astro_data: Dict):
    """Generate left metadata panel."""
    elements = []

    # Extract metadata
    meta = astro_data.get('meta', {})
    name = meta.get('name', 'Natal Chart')
    birth_date = meta.get('birth_date', '')
    birth_time = meta.get('birth_time', '')

    # Title
    elements.append(svg.text(
        20, 25,
        f"{name} - Birth Chart",
        font_size=FONT_SIZE_TITLE,
        fill='#000000',
        font_family=FONT_FAMILY,
        font_weight='600'
    ))

    # Birth info
    y_pos = 58
    if birth_date and birth_time:
        elements.append(svg.text(
            20, y_pos,
            f"{birth_date} • {birth_time}",
            font_size=FONT_SIZE_BODY,
            fill='#000000',
            font_family=FONT_FAMILY
        ))
        y_pos += 20

    # Angles
    angles = astro_data.get('angles', {})
    asc_data = angles.get('ascendant', {})
    mc_data = angles.get('midheaven', {})

    if asc_data:
        sign_to_index = {'Ari': 0, 'Tau': 1, 'Gem': 2, 'Can': 3, 'Leo': 4, 'Vir': 5,
                        'Lib': 6, 'Sco': 7, 'Sag': 8, 'Cap': 9, 'Aqu': 10, 'Pis': 11}
        asc_sign = asc_data.get('sign', 'Aqu')
        asc_pos = asc_data.get('position', 0)
        asc_abs = sign_to_index.get(asc_sign, 0) * 30 + asc_pos

        elements.append(svg.text(
            20, y_pos,
            f"ASC: {format_degree_full(asc_abs)}",
            font_size=FONT_SIZE_BODY,
            fill='#000000',
            font_family=FONT_FAMILY
        ))
        y_pos += 15

    if mc_data:
        sign_to_index = {'Ari': 0, 'Tau': 1, 'Gem': 2, 'Can': 3, 'Leo': 4, 'Vir': 5,
                        'Lib': 6, 'Sco': 7, 'Sag': 8, 'Cap': 9, 'Aqu': 10, 'Pis': 11}
        mc_sign = mc_data.get('sign', 'Sag')
        mc_pos = mc_data.get('position', 0)
        mc_abs = sign_to_index.get(mc_sign, 0) * 30 + mc_pos

        elements.append(svg.text(
            20, y_pos,
            f"MC: {format_degree_full(mc_abs)}",
            font_size=FONT_SIZE_BODY,
            fill='#000000',
            font_family=FONT_FAMILY
        ))

    svg.add(svg.group(elements, id='metadata'))


def generate_planet_grid(svg: SVGBuilder, planets_data: Dict):
    """Generate right-side planet position grid."""
    elements = []

    x_base = 685
    y_base = 70
    row_height = 14

    y_pos = y_base
    for planet_name, planet_info in planets_data.items():
        position = planet_info['position']
        is_retrograde = planet_info.get('retrograde', False)

        display_name = PLANET_NAMES.get(planet_name, planet_name)
        symbol = PLANET_SYMBOLS.get(planet_name, '?')
        color = PLANET_COLORS.get(planet_name, '#000000')
        sign_name = get_zodiac_sign_name(position)
        sign_symbol = ZODIAC_SYMBOLS[sign_name]

        # Planet name
        elements.append(svg.text(
            x_base, y_pos,
            display_name,
            font_size=FONT_SIZE_BODY,
            fill='#000000',
            text_anchor='end',
            font_family=FONT_FAMILY
        ))

        # Planet symbol
        elements.append(svg.text(
            x_base + 7, y_pos,
            symbol,
            font_size=12,
            fill=color,
            font_family=FONT_FAMILY
        ))

        # Position (degree'minute"second)
        position_text = format_degree_full(position)
        elements.append(svg.text(
            x_base + 23, y_pos,
            position_text,
            font_size=FONT_SIZE_BODY,
            fill='#000000',
            text_anchor='start',
            font_family=FONT_FAMILY
        ))

        # Sign symbol
        elements.append(svg.text(
            x_base + 95, y_pos,
            sign_symbol,
            font_size=11,
            fill=ZODIAC_COLORS[sign_name],
            font_family=FONT_FAMILY
        ))

        # Retrograde indicator
        if is_retrograde:
            elements.append(svg.text(
                x_base + 110, y_pos - 1,
                'Rx',
                font_size=7,
                fill=color,
                font_style='italic',
                font_family=FONT_FAMILY
            ))

        y_pos += row_height

    svg.add(svg.group(elements, id='planet_grid'))


# ============================================================================
# Main Entry Point
# ============================================================================

def generate_natal_chart_svg(astro_data: Dict) -> str:
    """Generate complete natal chart as pure SVG."""
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
            house_cusps.append((i - 1) * 30)

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
    generate_metadata_panel(svg, astro_data)
    generate_zodiac_wheel(svg)
    generate_house_cusps(svg, house_cusps)
    generate_aspects(svg, planets_data)
    generate_planets(svg, planets_data)
    generate_planet_grid(svg, planets_data)

    # Build final SVG
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{CANVAS_WIDTH}"
     height="{CANVAS_HEIGHT}"
     viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}">
    <title>Natal Chart</title>

    <style>
        text {{ font-family: {FONT_FAMILY}; }}
        .aspect {{ stroke-linecap: round; }}
    </style>

    <!-- Background -->
    <rect width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" fill="#ffffff"/>

    <!-- Chart Elements -->
    {chr(10).join('    ' + el for el in svg.elements)}
</svg>'''

    return svg_content


def render_natal_chart_svg(astro_data: Dict) -> bytes:
    """Main entry point for SVG generation."""
    svg_string = generate_natal_chart_svg(astro_data)
    return svg_string.encode('utf-8')
