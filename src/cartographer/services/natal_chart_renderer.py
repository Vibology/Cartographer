"""
Custom Natal Chart Renderer - Luminous/Ethereal Style
------------------------------------------------------
Renders traditional natal charts with circular zodiac wheel.
Matches the aesthetic of the bodygraph renderer.

Phase 1: Basic wheel geometry, zodiac divisions, house cusps
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

# Canvas dimensions
CANVAS_SIZE = 700  # Square canvas
CENTER_X = CANVAS_SIZE / 2
CENTER_Y = CANVAS_SIZE / 2
CHART_RADIUS = 280  # Outer edge of chart
ZODIAC_RING_WIDTH = 40  # Width of zodiac sign ring
HOUSE_RING_INNER = 80  # Inner edge of house ring (center of chart)


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


def generate_natal_chart_image(
    astro_data: dict,
    layout: str = "square",
    fmt: str = "svg"
) -> bytes:
    """
    Generate natal chart visualization.

    Args:
        astro_data: Astrology data from get_astro_data.py (Kerykeion format)
        layout: "square" (700×700) for now, more options in later phases
        fmt: Output format ("svg", "png")

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

    # Draw zodiac wheel
    draw_zodiac_wheel(ax, CENTER_X, CENTER_Y, CHART_RADIUS, ZODIAC_RING_WIDTH)

    # Draw house cusps
    inner_radius = CHART_RADIUS - ZODIAC_RING_WIDTH  # Inside zodiac ring
    draw_house_cusps(ax, CENTER_X, CENTER_Y, house_cusps, HOUSE_RING_INNER, inner_radius)

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
