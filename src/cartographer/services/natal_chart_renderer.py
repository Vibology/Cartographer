"""
Custom Natal Chart Renderer - Luminous/Ethereal Style
------------------------------------------------------
Renders traditional natal charts with circular zodiac wheel.
Matches the aesthetic of the bodygraph renderer.

Phase 1: Basic wheel geometry, zodiac divisions, house cusps
Phase 2: Planetary positions, symbols, degree labels
Phase 3: Aspect lines, metadata panel, final polish
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
from matplotlib.patches import Circle, Arc, Wedge, FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import io
import os

# --- FONT CONFIGURATION ---
def setup_fonts():
    """Register SF Pro fonts with matplotlib from macOS system paths."""
    sf_pro_paths = [
        '/System/Library/Fonts/',
        '/Library/Fonts/',
        os.path.expanduser('~/Library/Fonts/'),
    ]
    try:
        for font_dir in sf_pro_paths:
            if os.path.isdir(font_dir):
                for fname in os.listdir(font_dir):
                    if 'SF' in fname and fname.endswith(('.ttf', '.otf')):
                        fm.fontManager.addfont(os.path.join(font_dir, fname))
    except Exception as e:
        print(f"Warning: Could not load SF Pro fonts: {e}")

setup_fonts()

# Typography settings
FONT_FAMILY = 'SF Pro'
FONT_FALLBACK = 'Helvetica Neue'
FONT_SYMBOLS = 'DejaVu Sans'  # Good Unicode symbol support

def get_font():
    """Get the best available font for text."""
    sf_fonts = [f for f in fm.fontManager.ttflist if 'SF Pro' in f.name]
    if sf_fonts:
        return FONT_FAMILY
    hn_fonts = [f for f in fm.fontManager.ttflist if 'Helvetica Neue' in f.name]
    return FONT_FALLBACK if hn_fonts else 'DejaVu Sans'

def get_symbol_font():
    """Get font for astrological symbols (good Unicode coverage)."""
    return FONT_SYMBOLS

# --- COLOR PALETTE ---
# Luminous theme matching bodygraph
COLOR_BG_GRADIENT_START = "#FDFEFE"
COLOR_BG_GRADIENT_END = "#F4F6F7"
COLOR_WHEEL_STROKE = "#D5D8DC"
COLOR_WHEEL_FILL = "#FFFFFF"
COLOR_SIGN_TEXT = "#5D6D7E"
COLOR_HOUSE_LINE = "#A9B7C6"
COLOR_DEGREE_TEXT = "#7F8C8D"

# Zodiac sign symbols (Unicode)
ZODIAC_SYMBOLS = {
    'Aries': '♈',
    'Taurus': '♉',
    'Gemini': '♊',
    'Cancer': '♋',
    'Leo': '♌',
    'Virgo': '♍',
    'Libra': '♎',
    'Scorpio': '♏',
    'Sagittarius': '♐',
    'Capricorn': '♑',
    'Aquarius': '♒',
    'Pisces': '♓'
}

ZODIAC_ORDER = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Planet symbols (Unicode)
PLANET_SYMBOLS = {
    'Sun': '☉',
    'Moon': '☽',
    'Mercury': '☿',
    'Venus': '♀',
    'Mars': '♂',
    'Jupiter': '♃',
    'Saturn': '♄',
    'Uranus': '⛢',
    'Neptune': '♆',
    'Pluto': '♇',
    'True_North_Lunar_Node': '☊',
    'Mean_Lilith': '⚸',
    'Chiron': '⚷'
}

# Planet display order and colors
PLANET_ORDER = [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
    'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'
]

# Planet color coding (optional, can use monochrome)
PLANET_COLORS = {
    'Sun': '#F39C12',      # Gold
    'Moon': '#95A5A6',     # Silver
    'Mercury': '#3498DB',  # Blue
    'Venus': '#E91E63',    # Pink
    'Mars': '#E74C3C',     # Red
    'Jupiter': '#9B59B6',  # Purple
    'Saturn': '#34495E',   # Dark gray
    'Uranus': '#1ABC9C',   # Teal
    'Neptune': '#16A085',  # Sea green
    'Pluto': '#2C3E50'     # Almost black
}

# Aspect definitions (angle, orb, symbol, color)
ASPECTS = {
    'conjunction': {'angle': 0, 'orb': 8, 'symbol': '☌', 'color': '#E74C3C', 'linewidth': 2.0},
    'sextile': {'angle': 60, 'orb': 6, 'symbol': '⚹', 'color': '#3498DB', 'linewidth': 1.0},
    'square': {'angle': 90, 'orb': 8, 'symbol': '□', 'color': '#E67E22', 'linewidth': 1.5},
    'trine': {'angle': 120, 'orb': 8, 'symbol': '△', 'color': '#27AE60', 'linewidth': 1.5},
    'opposition': {'angle': 180, 'orb': 8, 'symbol': '☍', 'color': '#8E44AD', 'linewidth': 2.0}
}

# Canvas dimensions
CANVAS_SIZE = 780  # Square canvas (increased for metadata padding)
METADATA_HEIGHT = 70  # Height of metadata panel
METADATA_PADDING = 10  # Padding around metadata
CENTER_X = CANVAS_SIZE / 2
CENTER_Y = (CANVAS_SIZE + METADATA_HEIGHT) / 2  # Offset center down for metadata space
CHART_RADIUS = 280  # Outer edge of chart
ZODIAC_RING_WIDTH = 40  # Width of zodiac sign ring
HOUSE_RING_INNER = 80  # Inner edge of house ring (center of chart)
PLANET_RING_RADIUS = 200  # Radius for planet symbols (between houses and zodiac)


def draw_background_gradient(ax, size):
    """Draw a subtle gradient background."""
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack([gradient] * 256)

    cmap = LinearSegmentedColormap.from_list('bg', [COLOR_BG_GRADIENT_START, COLOR_BG_GRADIENT_END])

    ax.imshow(
        gradient.T,
        aspect='auto',
        cmap=cmap,
        extent=[0, size, size, 0],
        zorder=-10,
        alpha=0.5
    )


def draw_zodiac_wheel(ax, center_x, center_y, outer_radius, ring_width):
    """
    Draw the zodiac wheel with 12 sign divisions.

    In traditional astrology charts:
    - 0° Aries starts at 9 o'clock position (left, 180° in matplotlib coordinates)
    - Signs progress counter-clockwise
    - Each sign occupies 30°
    """
    font = get_font()
    inner_radius = outer_radius - ring_width

    # Draw outer circle (zodiac ring)
    outer_circle = Circle(
        (center_x, center_y),
        radius=outer_radius,
        facecolor='none',
        edgecolor=COLOR_WHEEL_STROKE,
        linewidth=2.0,
        zorder=10
    )
    ax.add_patch(outer_circle)

    # Draw inner circle (house ring boundary)
    inner_circle = Circle(
        (center_x, center_y),
        radius=inner_radius,
        facecolor=COLOR_WHEEL_FILL,
        edgecolor=COLOR_WHEEL_STROKE,
        linewidth=1.5,
        zorder=10
    )
    ax.add_patch(inner_circle)

    # Draw zodiac sign divisions and symbols
    # Start at 180° (9 o'clock) for 0° Aries, proceed counter-clockwise
    for i, sign_name in enumerate(ZODIAC_ORDER):
        # Angle for this sign (matplotlib uses degrees, 0° = right, counter-clockwise)
        # We want 0° Aries at left (180°), then go counter-clockwise
        start_angle = 180 - (i * 30)  # Start of this sign
        end_angle = start_angle - 30   # End of this sign (30° span, counter-clockwise)

        # Draw division line between signs
        angle_rad = np.radians(start_angle)
        x1 = center_x + inner_radius * np.cos(angle_rad)
        y1 = center_y + inner_radius * np.sin(angle_rad)
        x2 = center_x + outer_radius * np.cos(angle_rad)
        y2 = center_y + outer_radius * np.sin(angle_rad)

        ax.plot(
            [x1, x2], [y1, y2],
            color=COLOR_WHEEL_STROKE,
            linewidth=1.0,
            zorder=11
        )

        # Place zodiac symbol at midpoint of sign arc
        mid_angle = start_angle - 15  # Midpoint of 30° span
        mid_angle_rad = np.radians(mid_angle)
        symbol_radius = outer_radius - (ring_width / 2)

        symbol_x = center_x + symbol_radius * np.cos(mid_angle_rad)
        symbol_y = center_y + symbol_radius * np.sin(mid_angle_rad)

        ax.text(
            symbol_x, symbol_y,
            ZODIAC_SYMBOLS[sign_name],
            fontsize=20,
            ha='center',
            va='center',
            color=COLOR_SIGN_TEXT,
            fontfamily=get_symbol_font(),  # Use symbol font for glyphs
            zorder=12
        )

        # Add degree markers at 0° and 15° of each sign (optional, for reference)
        # 0° marker at start of sign
        degree_radius = outer_radius - ring_width + 8
        deg_x = center_x + degree_radius * np.cos(angle_rad)
        deg_y = center_y + degree_radius * np.sin(angle_rad)

        ax.text(
            deg_x, deg_y,
            '0°',
            fontsize=7,
            ha='center',
            va='center',
            color=COLOR_DEGREE_TEXT,
            fontfamily=font,
            alpha=0.6,
            zorder=12
        )


def draw_house_cusps(ax, center_x, center_y, house_cusps, inner_radius, outer_radius):
    """
    Draw house cusp lines radiating from center.

    Args:
        house_cusps: List of 12 house cusp positions in degrees (0-360, zodiac longitude)
        inner_radius: Inner edge of house ring
        outer_radius: Outer edge where house lines reach
    """
    font = get_font()

    for i, cusp_degree in enumerate(house_cusps):
        house_number = i + 1

        # Convert zodiac longitude to matplotlib angle
        # Zodiac 0° = 180° matplotlib (9 o'clock), counter-clockwise
        # Zodiac increases counter-clockwise, matplotlib increases counter-clockwise
        # So: matplotlib_angle = 180° - zodiac_longitude
        angle_matplotlib = 180 - cusp_degree
        angle_rad = np.radians(angle_matplotlib)

        # Draw cusp line from inner radius to outer radius
        x1 = center_x + inner_radius * np.cos(angle_rad)
        y1 = center_y + inner_radius * np.sin(angle_rad)
        x2 = center_x + outer_radius * np.cos(angle_rad)
        y2 = center_y + outer_radius * np.sin(angle_rad)

        # Cusp 1 (Ascendant), 4 (IC), 7 (Descendant), 10 (MC) are thicker
        angular_houses = [1, 4, 7, 10]
        linewidth = 2.0 if house_number in angular_houses else 1.0
        alpha = 0.9 if house_number in angular_houses else 0.6

        ax.plot(
            [x1, x2], [y1, y2],
            color=COLOR_HOUSE_LINE,
            linewidth=linewidth,
            alpha=alpha,
            zorder=11
        )

        # Place house number near inner radius
        number_radius = inner_radius + 25
        num_x = center_x + number_radius * np.cos(angle_rad)
        num_y = center_y + number_radius * np.sin(angle_rad)

        ax.text(
            num_x, num_y,
            str(house_number),
            fontsize=11,
            ha='center',
            va='center',
            color=COLOR_HOUSE_LINE,
            fontfamily=font,
            fontweight='bold' if house_number in angular_houses else 'normal',
            zorder=13
        )


def draw_planets(ax, center_x, center_y, planets_data, planet_radius):
    """
    Draw planet symbols and degree labels at their zodiac positions.

    Args:
        planets_data: Dict of planet positions from astro_calculator
                      Format: {'Sun': {'position': 24.532, 'sign': 'Gemini', 'retrograde': False}, ...}
        planet_radius: Radius from center where planets are placed
    """
    font = get_font()
    symbol_font = get_symbol_font()

    # Track placed planets for collision detection
    placed_positions = []

    for planet_name in PLANET_ORDER:
        if planet_name not in planets_data:
            continue

        planet_info = planets_data[planet_name]
        zodiac_longitude = planet_info.get('position', 0)  # 0-360 degrees
        is_retrograde = planet_info.get('retrograde', False)

        # Convert zodiac longitude to matplotlib angle
        # Zodiac 0° = 180° matplotlib (9 o'clock), counter-clockwise
        angle_matplotlib = 180 - zodiac_longitude
        angle_rad = np.radians(angle_matplotlib)

        # Check for collisions and adjust radius if needed
        adjusted_radius = planet_radius
        collision_detected = False

        for placed_angle, placed_radius in placed_positions:
            angle_diff = abs(angle_matplotlib - placed_angle)
            # Normalize to 0-180 range
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            # If planets are within 15° of each other, offset the radius
            if angle_diff < 15:
                collision_detected = True
                # Alternate between inner and outer positions
                if len([p for p in placed_positions if abs(p[0] - angle_matplotlib) < 15]) % 2 == 0:
                    adjusted_radius = planet_radius - 25
                else:
                    adjusted_radius = planet_radius + 25
                break

        # Calculate planet position
        planet_x = center_x + adjusted_radius * np.cos(angle_rad)
        planet_y = center_y + adjusted_radius * np.sin(angle_rad)

        # Get planet color
        planet_color = PLANET_COLORS.get(planet_name, '#34495E')

        # Draw planet symbol
        symbol = PLANET_SYMBOLS.get(planet_name, '?')
        ax.text(
            planet_x, planet_y,
            symbol,
            fontsize=18,
            ha='center',
            va='center',
            color=planet_color,
            fontfamily=symbol_font,
            fontweight='bold',
            zorder=15
        )

        # Add retrograde indicator if applicable
        if is_retrograde:
            rx_x = planet_x + 12
            rx_y = planet_y - 8
            ax.text(
                rx_x, rx_y,
                'Rx',
                fontsize=7,
                ha='left',
                va='top',
                color=planet_color,
                fontfamily=font,
                style='italic',
                alpha=0.8,
                zorder=15
            )

        # Add degree label
        # Format: degree and minute (e.g., "24°32'")
        degree = int(zodiac_longitude % 30)  # Degree within sign (0-29)
        minute = int((zodiac_longitude % 1) * 60)  # Minute within degree
        degree_label = f"{degree}°{minute:02d}'"

        # Position label slightly inside the planet
        label_radius = adjusted_radius - 30
        label_x = center_x + label_radius * np.cos(angle_rad)
        label_y = center_y + label_radius * np.sin(angle_rad)

        ax.text(
            label_x, label_y,
            degree_label,
            fontsize=8,
            ha='center',
            va='center',
            color=planet_color,
            fontfamily=font,
            alpha=0.9,
            zorder=14
        )

        # Record this planet's position for collision detection
        placed_positions.append((angle_matplotlib, adjusted_radius))


def calculate_aspect_angle(pos1, pos2):
    """
    Calculate the angular distance between two zodiac positions.
    Returns the smallest angle (0-180 degrees).
    """
    diff = abs(pos1 - pos2)
    # Normalize to 0-180 range (shortest distance around the circle)
    if diff > 180:
        diff = 360 - diff
    return diff


def find_aspects(planets_data):
    """
    Find all major aspects between planets.

    Returns:
        List of tuples: (planet1_name, planet2_name, aspect_type, exact_angle)
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

                # Calculate difference from exact aspect
                diff = abs(angle - target_angle)

                if diff <= orb:
                    aspects_found.append((
                        planet1,
                        planet2,
                        aspect_name,
                        angle
                    ))
                    break  # Found an aspect, don't check others

    return aspects_found


def draw_aspects(ax, center_x, center_y, planets_data, aspect_radius):
    """
    Draw aspect lines connecting planets.

    Args:
        planets_data: Dict of planet positions
        aspect_radius: Radius for aspect line endpoints (slightly inside planet positions)
    """
    aspects = find_aspects(planets_data)

    for planet1, planet2, aspect_type, angle in aspects:
        # Get positions
        pos1 = planets_data[planet1]['position']
        pos2 = planets_data[planet2]['position']

        # Convert to matplotlib angles
        angle1_rad = np.radians(180 - pos1)
        angle2_rad = np.radians(180 - pos2)

        # Calculate line endpoints
        x1 = center_x + aspect_radius * np.cos(angle1_rad)
        y1 = center_y + aspect_radius * np.sin(angle1_rad)
        x2 = center_x + aspect_radius * np.cos(angle2_rad)
        y2 = center_y + aspect_radius * np.sin(angle2_rad)

        # Get aspect styling
        aspect_info = ASPECTS[aspect_type]
        color = aspect_info['color']
        linewidth = aspect_info['linewidth']

        # Draw aspect line
        ax.plot(
            [x1, x2], [y1, y2],
            color=color,
            linewidth=linewidth,
            alpha=0.6,  # More visible (was 0.4)
            zorder=8,  # Behind planets (10+) but above wheel (5-7)
            linestyle='-'
        )


def draw_metadata_panel(ax, astro_data, canvas_width, y_position):
    """
    Draw metadata panel with birth data and chart information.

    Args:
        astro_data: Full astrology data
        canvas_width: Width of canvas
        y_position: Y position for top of panel
    """
    font = get_font()

    # Extract metadata
    name = astro_data.get('name', 'Natal Chart')
    birth_data = astro_data.get('birth_data', {})
    houses = astro_data.get('houses', {})

    # Format birth date/time
    if birth_data:
        date_str = birth_data.get('date', '')
        time_str = birth_data.get('time', '')
        location = birth_data.get('location', '')
        birth_info = f"{date_str} • {time_str} • {location}"
    else:
        birth_info = ""

    # Get ASC and MC
    asc_degree = houses.get('house_1', 0)
    mc_degree = houses.get('house_10', 0)

    # Convert to sign and degree
    def format_zodiac_position(longitude):
        signs = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir',
                'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']
        sign_index = int(longitude / 30)
        degree = int(longitude % 30)
        minute = int((longitude % 1) * 60)
        return f"{degree}°{minute:02d}' {signs[sign_index]}"

    asc_str = format_zodiac_position(asc_degree)
    mc_str = format_zodiac_position(mc_degree)

    # Panel background
    panel_height = 65
    panel = FancyBboxPatch(
        (15, y_position),
        canvas_width - 30,
        panel_height,
        boxstyle="round,pad=0.02,rounding_size=6",
        facecolor='#FAFBFC',
        edgecolor='#E8EBED',
        linewidth=1.5,
        alpha=0.95,
        zorder=20
    )
    ax.add_patch(panel)

    # Name (centered, top)
    ax.text(
        canvas_width / 2,
        y_position + 15,
        name,
        fontsize=14,
        fontweight='bold',
        ha='center',
        va='center',
        color='#2C3E50',
        fontfamily=font,
        zorder=21
    )

    # Birth info (centered, middle)
    if birth_info:
        ax.text(
            canvas_width / 2,
            y_position + 32,
            birth_info,
            fontsize=9,
            ha='center',
            va='center',
            color='#7F8C8D',
            fontfamily=font,
            zorder=21
        )

    # ASC and MC (bottom corners)
    ax.text(
        30,
        y_position + 48,
        f"ASC: {asc_str}",
        fontsize=9,
        ha='left',
        va='center',
        color='#34495E',
        fontfamily=font,
        fontweight='bold',
        zorder=21
    )

    ax.text(
        canvas_width - 30,
        y_position + 48,
        f"MC: {mc_str}",
        fontsize=9,
        ha='right',
        va='center',
        color='#34495E',
        fontfamily=font,
        fontweight='bold',
        zorder=21
    )


def generate_natal_chart_image(
    astro_data: dict,
    layout: str = "square",
    fmt: str = "svg",
    include_aspects: bool = True,
    include_metadata: bool = True
) -> bytes:
    """
    Generate natal chart visualization.

    Args:
        astro_data: Astrology data from get_astro_data.py (Kerykeion format)
        layout: "square" (700×700) for now, more options in later phases
        fmt: Output format ("svg", "png")
        include_aspects: Draw aspect lines between planets
        include_metadata: Include metadata panel with birth data

    Returns:
        Image bytes
    """
    # Extract house cusps from astro data
    # Format from astro_calculator: {'house_1': 193.69, 'house_2': 220.77, ...}
    houses_data = astro_data.get('houses', {})
    house_cusps = []

    # Extract positions for houses 1-12
    for i in range(1, 13):
        house_key = f"house_{i}"
        if house_key in houses_data:
            house_cusps.append(houses_data[house_key])
        else:
            # Fallback: equal house system (30° per house, starting at 0°)
            house_cusps.append((i - 1) * 30)

    # Figure setup
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    ax.set_xlim(0, CANVAS_SIZE)
    ax.set_ylim(CANVAS_SIZE, 0)  # Invert Y axis
    ax.axis('off')

    # Background
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    draw_background_gradient(ax, CANVAS_SIZE)

    # Draw metadata panel first (at top)
    if include_metadata:
        draw_metadata_panel(ax, astro_data, CANVAS_SIZE, METADATA_PADDING)

    # Draw zodiac wheel
    draw_zodiac_wheel(ax, CENTER_X, CENTER_Y, CHART_RADIUS, ZODIAC_RING_WIDTH)

    # Draw house cusps
    inner_radius = CHART_RADIUS - ZODIAC_RING_WIDTH  # Inside zodiac ring
    draw_house_cusps(ax, CENTER_X, CENTER_Y, house_cusps, HOUSE_RING_INNER, inner_radius)

    # Extract and draw planets
    # astro_data format: {'planets': [{'name': 'Sun', 'longitude': 84.38, ...}, ...]}
    planets_list = astro_data.get('planets', [])
    planets_data = {}
    if planets_list:
        # Convert list to dict keyed by planet name
        for planet in planets_list:
            planet_name = planet.get('name', '')
            if planet_name:
                planets_data[planet_name] = {
                    'position': planet.get('longitude', 0),
                    'sign': planet.get('sign', ''),
                    'retrograde': planet.get('retrograde', False)
                }

        # Draw aspect lines (behind planets)
        if include_aspects and len(planets_data) > 1:
            # Place aspect endpoints between center and planet positions
            aspect_radius = PLANET_RING_RADIUS - 30  # Slightly inside planet ring
            draw_aspects(ax, CENTER_X, CENTER_Y, planets_data, aspect_radius)

        # Draw planets (on top of aspects)
        draw_planets(ax, CENTER_X, CENTER_Y, planets_data, PLANET_RING_RADIUS)

    # Save to buffer
    buf = io.BytesIO()
    if fmt.lower() == 'svg':
        fig.savefig(buf, format='svg', bbox_inches='tight', pad_inches=0.1, transparent=True)
    else:  # PNG
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1,
                   transparent=True, dpi=150)

    plt.close(fig)
    buf.seek(0)
    return buf.read()


# --- Standalone testing ---
if __name__ == "__main__":
    # Test data with sample house cusps
    test_data = {
        "houses": [
            {"name": "First_House", "position": 0},
            {"name": "Second_House", "position": 30},
            {"name": "Third_House", "position": 60},
            {"name": "Fourth_House", "position": 90},
            {"name": "Fifth_House", "position": 120},
            {"name": "Sixth_House", "position": 150},
            {"name": "Seventh_House", "position": 180},
            {"name": "Eighth_House", "position": 210},
            {"name": "Ninth_House", "position": 240},
            {"name": "Tenth_House", "position": 270},
            {"name": "Eleventh_House", "position": 300},
            {"name": "Twelfth_House", "position": 330}
        ]
    }

    img_bytes = generate_natal_chart_image(test_data, fmt='png')
    with open("natal_chart_phase1.png", "wb") as f:
        f.write(img_bytes)
    print("Phase 1 test chart saved to natal_chart_phase1.png")
