"""
Enhanced Bodygraph Chart Renderer - Luminous/Ethereal Style
------------------------------------------------------------
Renders Human Design bodygraph charts with:
- Luminous gradient fills for defined centers
- Soft glow effects emanating from centers
- Ethereal body silhouette
- SF Pro typography
- Planetary activation side panels
- Summary information panel
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
from matplotlib.colors import LinearSegmentedColormap, to_rgba
import matplotlib.transforms
from matplotlib.patches import FancyBboxPatch, Circle, PathPatch, Polygon
import matplotlib.font_manager as fm
from svgpath2mpl import parse_path
import numpy as np
import json
import io
import os
import importlib.resources
import base64
import xml.etree.ElementTree as ET
from PIL import Image

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
FONT_SYMBOLS = 'DejaVu Sans Mono'  # Monospace for consistent glyph alignment

def get_font():
    """Get the best available font for text."""
    sf_fonts = [f for f in fm.fontManager.ttflist if 'SF Pro' in f.name]
    if sf_fonts:
        return FONT_FAMILY
    # Try Helvetica Neue as secondary fallback (always available on macOS)
    hn_fonts = [f for f in fm.fontManager.ttflist if 'Helvetica Neue' in f.name]
    return FONT_FALLBACK if hn_fonts else 'DejaVu Sans'

def get_symbol_font():
    """Get font for astrological symbols (monospace ensures consistent alignment)."""
    return FONT_SYMBOLS

# --- CONFIGURATION ---
LAYOUT_FILE = "layout_data.json"
EXALTATIONS_FILE = "exaltations_detriments.json"

# Luminous Chakra Color Palette - Light Mode (Traditional HD colors)
CENTER_COLORS = {
    "Head": {
        "defined": "#B57EDC",      # Soft violet
        "glow": "#E8D5F2",         # Light violet glow
        "stroke": "#8B5DC2",
    },
    "Ajna": {
        "defined": "#7B8FB8",      # Indigo-gray
        "glow": "#C5D0E8",         # Light indigo glow
        "stroke": "#5D6D8E",
    },
    "Throat": {
        "defined": "#5DADE2",      # Sky blue
        "glow": "#D4EDFC",         # Light blue glow
        "stroke": "#3498DB",
    },
    "G": {
        "defined": "#F7DC6F",      # Warm gold
        "glow": "#FDF5D6",         # Light gold glow
        "stroke": "#D4AC0D",
    },
    "Heart": {
        "defined": "#82E0AA",      # Soft green
        "glow": "#D5F5E3",         # Light green glow
        "stroke": "#28B463",
    },
    "SolarPlexus": {
        "defined": "#F8C471",      # Warm amber
        "glow": "#FDEBD0",         # Light amber glow
        "stroke": "#E67E22",
    },
    "Spleen": {
        "defined": "#73C6B6",      # Teal
        "glow": "#D0ECE7",         # Light teal glow
        "stroke": "#1ABC9C",
    },
    "Sacral": {
        "defined": "#F1948A",      # Soft coral
        "glow": "#FADBD8",         # Light coral glow
        "stroke": "#E74C3C",
    },
    "Root": {
        "defined": "#A67B5B",      # Earthy brown
        "glow": "#D7C4B7",         # Light brown glow
        "stroke": "#8B5A2B",
    },
}

# Dark Mode Center Colors - Rich jewel tones (muted but beautiful)
# Philosophy: Deep, sophisticated colors that don't compete with activations
# Think: Aged stained glass, gemstones, velvet - rich but restrained
DARK_CENTER_COLORS = {
    "Head": {
        "defined": "#AA77DD",      # Deep amethyst (rich violet, not bright purple)
        "glow": "#BB88DD",         # Subtle violet glow
        "stroke": "#9966CC",
    },
    "Ajna": {
        "defined": "#8899CC",      # Deep indigo (rich blue-purple, not bright)
        "glow": "#99AADD",         # Subtle indigo glow
        "stroke": "#7788BB",
    },
    "Throat": {
        "defined": "#6699DD",      # Deep cerulean (rich sky blue, not electric)
        "glow": "#77AAEE",         # Subtle blue glow
        "stroke": "#5588CC",
    },
    "G": {
        "defined": "#EEBB66",      # Deep gold (rich warm yellow, not neon)
        "glow": "#FFCC77",         # Subtle gold glow
        "stroke": "#DDAA55",
    },
    "Heart": {
        "defined": "#77CC99",      # Deep emerald (rich green, not bright)
        "glow": "#88DDAA",         # Subtle green glow
        "stroke": "#66BB88",
    },
    "SolarPlexus": {
        "defined": "#EEBB77",      # Deep amber (rich warm orange, not bright)
        "glow": "#FFCC88",         # Subtle amber glow
        "stroke": "#DDAA66",
    },
    "Spleen": {
        "defined": "#66BBAA",      # Deep jade (rich teal, not electric)
        "glow": "#77CCBB",         # Subtle teal glow
        "stroke": "#55AA99",
    },
    "Sacral": {
        "defined": "#EE9988",      # Deep coral (rich warm orange-pink, not neon)
        "glow": "#FFAA99",         # Subtle coral glow
        "stroke": "#DD8877",
    },
    "Root": {
        "defined": "#BB8866",      # Deep sienna (rich earth tone, not pale)
        "glow": "#CC9977",         # Subtle brown glow
        "stroke": "#AA7755",
    },
}

UNDEFINED_CENTER = {
    "fill": "#FDFEFE",
    "stroke": "#D5D8DC",
    "glow": None
}

DARK_UNDEFINED_CENTER = {
    "fill": "#252525",
    "stroke": "#404040",
    "glow": None
}

# Channel and Gate Colors (Light Mode)
COLOR_DESIGN = "#C0392B"       # Deep crimson for Design
COLOR_PERSONALITY = "#2C3E50"  # Deep slate for Personality
COLOR_BODY_BG = "#E8E8E8"      # Soft gray body
COLOR_BODY_STROKE = "#BDC3C7"
COLOR_CHANNEL_INACTIVE = "#C8CDD2"  # More visible gray for undefined channels
COLOR_CHANNEL_GLOW = "#D6DBDF"

# Background (Light Mode)
COLOR_BG_GRADIENT_START = "#FDFEFE"
COLOR_BG_GRADIENT_END = "#F4F6F7"

# Dark Mode Colors (Comprehensive luminous redesign)
# Body & Structure
DARK_BODY_BG = "#404040"           # Medium gray - visible structure
DARK_BODY_STROKE = "#808080"       # Bright outline - clearly defined
DARK_BODY_GLOW_1 = "#555555"       # Stronger outer glow
DARK_BODY_GLOW_2 = "#4A4A4A"       # Stronger inner glow

# Channels
DARK_CHANNEL_INACTIVE = "#888888"  # Quite visible - shows anatomy
DARK_CHANNEL_GLOW = "#666666"      # Subtle luminosity

# Centers
DARK_UNDEFINED_CENTER_FILL = "#2A2A2A"  # Darker than body - creates depth
DARK_UNDEFINED_CENTER_STROKE = "#606060"  # Visible borders

# Gate Numbers
DARK_GATE_INACTIVE_COLOR = "#CCCCCC"   # Very light gray for inactive gates on dark background
# Note: Active gates always use black text (#1A1A1A) on white circles in both modes

# Background
DARK_BG_GRADIENT_START = "#1A1A1A"
DARK_BG_GRADIENT_END = "#242424"

# Panel Text Colors (Luminous accents - non-overlapping with center colors)
DARK_DESIGN_TEXT = "#FF40BF"       # Pure magenta (distinct from all centers)
DARK_DESIGN_HEADER = "#FF66CC"     # Bright magenta
DARK_PERSONALITY_TEXT = "#4488FF"  # Electric blue (distinct from all centers)
DARK_PERSONALITY_HEADER = "#66AAFF"  # Bright electric blue

# Canvas Dimensions
BODYGRAPH_W = 240
BODYGRAPH_H = 320  # Original height - matches SVG geometry
PANEL_WIDTH = 58
SUMMARY_HEIGHT = 0  # Summary panel disabled

# Planet Symbols
PLANET_SYMBOLS = {
    "Sun": "☉", "Earth": "⊕", "Moon": "☽",
    "North_Node": "☊", "South_Node": "☋",
    "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptune": "♆", "Pluto": "♇"
}

PLANET_ORDER = [
    "Sun", "Earth", "Moon", "North_Node", "South_Node",
    "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto"
]

# Strategy by Type
TYPE_STRATEGIES = {
    'Generator': 'Wait to Respond',
    'Manifesting Generator': 'Wait to Respond',
    'Projector': 'Wait for the Invitation',
    'Manifestor': 'Inform',
    'Reflector': 'Wait a Lunar Cycle'
}

# Channel to Centers mapping (which centers each channel connects)
CHANNEL_CENTERS = {
    '1-8': ('G', 'Throat'),
    '2-14': ('G', 'Sacral'),
    '3-60': ('Sacral', 'Root'),
    '4-63': ('Ajna', 'Head'),
    '5-15': ('Sacral', 'G'),
    '6-59': ('Sacral', 'SolarPlexus'),
    '7-31': ('G', 'Throat'),
    '9-52': ('Sacral', 'Root'),
    '10-20': ('G', 'Throat'),
    '10-34': ('G', 'Sacral'),
    '10-57': ('G', 'Spleen'),
    '11-56': ('Ajna', 'Throat'),
    '12-22': ('Throat', 'SolarPlexus'),
    '13-33': ('G', 'Throat'),
    '16-48': ('Throat', 'Spleen'),
    '17-62': ('Ajna', 'Throat'),
    '18-58': ('Spleen', 'Root'),
    '19-49': ('Root', 'SolarPlexus'),
    '20-34': ('Throat', 'Sacral'),
    '20-57': ('Throat', 'Spleen'),
    '21-45': ('Heart', 'Throat'),
    '23-43': ('Ajna', 'Throat'),
    '24-61': ('Ajna', 'Head'),
    '25-51': ('G', 'Heart'),
    '26-44': ('Heart', 'Spleen'),
    '27-50': ('Sacral', 'Spleen'),
    '28-38': ('Spleen', 'Root'),
    '29-46': ('Sacral', 'G'),
    '30-41': ('SolarPlexus', 'Root'),
    '32-54': ('Spleen', 'Root'),
    '34-57': ('Sacral', 'Spleen'),
    '35-36': ('Throat', 'SolarPlexus'),
    '37-40': ('SolarPlexus', 'Heart'),
    '39-55': ('Root', 'SolarPlexus'),
    '42-53': ('Sacral', 'Root'),
    '47-64': ('Ajna', 'Head'),
}

def get_strategy_from_type(energy_type):
    """Get the strategy for a given energy type."""
    return TYPE_STRATEGIES.get(energy_type, 'Unknown')

def normalize_center_name(name):
    """Normalize center names to match internal naming (G_Center -> G, etc.)."""
    name_map = {
        'G_Center': 'G',
        'G Center': 'G',
        'g_center': 'G',
        'g center': 'G',
        'g': 'G',
        'Anja': 'Ajna',  # Common typo
        'Solar Plexus': 'SolarPlexus',
        'solar plexus': 'SolarPlexus',
        'solarplexus': 'SolarPlexus',
    }
    return name_map.get(name, name)

def derive_defined_centers(chart_data):
    """
    Derive defined centers from channels.
    Returns a set of center names that are defined.
    """
    defined = set()
    channels = chart_data.get('channels', [])

    for channel_info in channels:
        # Handle both dict format {'channel': '3-60'} and string format '3-60'
        if isinstance(channel_info, dict):
            channel = channel_info.get('channel', '')
        else:
            channel = str(channel_info)

        # Extract gate numbers from various formats:
        # "6/59: The Channel of Mating..." -> "6/59"
        # "6-59" -> "6-59"
        # "6/59" -> "6/59"
        if channel:
            # Take only the first part before any colon or description
            channel = channel.split(':')[0].strip()

            # Try both '/' and '-' as separators
            if '/' in channel:
                parts = channel.split('/')
            elif '-' in channel:
                parts = channel.split('-')
            else:
                continue

            if len(parts) == 2:
                try:
                    g1, g2 = int(parts[0].strip()), int(parts[1].strip())
                    normalized = f"{min(g1,g2)}-{max(g1,g2)}"
                    if normalized in CHANNEL_CENTERS:
                        c1, c2 = CHANNEL_CENTERS[normalized]
                        defined.add(c1)
                        defined.add(c2)
                except ValueError:
                    pass

    return defined

def ensure_chart_data_complete(chart_data):
    """
    Ensure chart_data has all necessary fields, deriving them if needed.
    Returns a new dict with complete data.
    """
    result = dict(chart_data)
    general = dict(result.get('general', {}))

    # Check for defined_centers in multiple possible locations/names
    defined_centers = None

    # First check 'defined_centers' directly
    if 'defined_centers' in general and general['defined_centers']:
        defined_centers = general['defined_centers']
    # Then check 'active_chakras' (API format)
    elif 'active_chakras' in general and general['active_chakras']:
        defined_centers = general['active_chakras']
    # Finally, derive from channels
    else:
        defined_centers = list(derive_defined_centers(chart_data))

    # Normalize all center names
    general['defined_centers'] = [normalize_center_name(c) for c in defined_centers]

    # Derive strategy if not present
    if 'strategy' not in general or not general['strategy']:
        energy_type = general.get('energy_type', '')
        general['strategy'] = get_strategy_from_type(energy_type)

    result['general'] = general
    return result


def load_json_layout():
    """Loads the SVG layout data from layout_data.json."""
    try:
        data_path = importlib.resources.files("cartographer.data").joinpath(LAYOUT_FILE)
        with data_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading layout file: {e}", file=sys.stderr)
        return {}


# Cache for exaltations data (loaded once)
_exaltations_cache = None

def load_exaltations_data():
    """Loads the exaltations/detriments data for planetary dignities."""
    global _exaltations_cache
    if _exaltations_cache is not None:
        return _exaltations_cache
    try:
        data_path = importlib.resources.files("cartographer.data").joinpath(EXALTATIONS_FILE)
        with data_path.open("r", encoding="utf-8") as f:
            _exaltations_cache = json.load(f)
            return _exaltations_cache
    except Exception as e:
        print(f"Error loading exaltations file: {e}")
        return {}


def find_planet_at_gate(planets_data, gate):
    """
    Find which planet activates a specific gate.

    Args:
        planets_data: List of planet dictionaries
        gate: Gate number to find

    Returns:
        Planet name if found, None otherwise
    """
    if not planets_data or gate == '–' or gate == 0:
        return None

    for planet in planets_data:
        if planet.get('Gate') == gate:
            return planet.get('Planet')
    return None


def find_planet_at_opposite_gate(gate, opposite_planets_data, is_current_design):
    """
    Find planet at gate on opposite side (for cross-aspect harmonic fixing).

    Args:
        gate: Gate number to find
        opposite_planets_data: Planet data from opposite side (Design if checking from Personality, or vice versa)
        is_current_design: Whether we're checking FROM design side

    Returns:
        Planet name if found, None otherwise
    """
    if not opposite_planets_data or gate == '–' or gate == 0:
        return None

    for planet in opposite_planets_data:
        if planet.get('Gate') == gate:
            return planet.get('Planet')
    return None


def get_planet_dignity(planet_name, gate, line, exaltations_data, harmonic_gate=None, harmonic_planet=None, gate_level_planets=None):
    """
    Determine dignity using full IHDS algorithm including harmonic and gate-level fixing.

    Args:
        planet_name: Active planet
        gate: Gate number
        line: Line number
        exaltations_data: Dignity data dictionary
        harmonic_gate: Harmonic partner gate (if in channel)
        harmonic_planet: Planet at harmonic gate (if any)
        gate_level_planets: List of all planets at this gate (any line, both aspects)

    Returns: 'exalted', 'detriment', 'juxtaposed', or None
    """
    from ..features.dignity import calculate_dignity

    if not exaltations_data or gate == '–' or line == '–':
        return None

    # Convert gate/line to integers
    try:
        gate_int = int(gate)
        line_int = int(line)
    except (ValueError, TypeError):
        return None

    result = calculate_dignity(
        gate=gate_int,
        line=line_int,
        active_planet=planet_name,
        harmonic_gate=harmonic_gate,
        harmonic_planet=harmonic_planet,
        dignity_data=exaltations_data,
        gate_level_planets=gate_level_planets
    )

    state = result.get("state")
    return state if state != "neutral" else None




def normalize_gates_data(chart_data):
    """
    Normalize gates data to consistent format.

    Handles both API format (des/prs with Planets list) and simple format (design/personality dict).
    Returns (design_gates_dict, personality_gates_dict, design_planets_list, personality_planets_list)
    """
    gates = chart_data.get('gates', {})

    # API format: {'des': {'Planets': [...]}, 'prs': {'Planets': [...]}}
    if 'des' in gates and isinstance(gates.get('des'), dict) and 'Planets' in gates.get('des', {}):
        des_planets = gates['des']['Planets']
        prs_planets = gates['prs']['Planets']
        design_gates = {g['Gate']: g for g in des_planets}
        personality_gates = {g['Gate']: g for g in prs_planets}
        return design_gates, personality_gates, des_planets, prs_planets

    # Simple format: {'design': [...], 'personality': [...]} (list or dict)
    elif 'design' in gates:
        design_raw = gates.get('design', [])
        personality_raw = gates.get('personality', [])

        # Convert to gate-indexed dicts
        design_gates = {}
        personality_gates = {}
        des_planets = []
        prs_planets = []

        # Handle list format: [{'planet': 'Sun', 'gate': X, 'line': Y, ...}, ...]
        if isinstance(design_raw, list):
            for item in design_raw:
                planet = item.get('planet', item.get('Planet', 'Unknown'))
                gate = item.get('gate', item.get('Gate'))
                if gate:
                    planet_data = {
                        'Planet': planet,
                        'Gate': gate,
                        'Line': item.get('line', item.get('Line', 1)),
                        'Tone': item.get('tone', item.get('Tone', 1)),
                        'zodiac_sign': item.get('zodiac_sign', '')
                    }
                    design_gates[gate] = planet_data
                    des_planets.append(planet_data)
        # Handle dict format: {'Sun': {'gate': X, 'line': Y}, ...}
        else:
            for planet, data in design_raw.items():
                gate = data.get('gate')
                if gate:
                    planet_data = {
                        'Planet': planet,
                        'Gate': gate,
                        'Line': data.get('line', 1),
                        'Tone': data.get('tone', 1)
                    }
                    design_gates[gate] = planet_data
                    des_planets.append(planet_data)

        # Handle list format for personality
        if isinstance(personality_raw, list):
            for item in personality_raw:
                planet = item.get('planet', item.get('Planet', 'Unknown'))
                gate = item.get('gate', item.get('Gate'))
                if gate:
                    planet_data = {
                        'Planet': planet,
                        'Gate': gate,
                        'Line': item.get('line', item.get('Line', 1)),
                        'Tone': item.get('tone', item.get('Tone', 1)),
                        'zodiac_sign': item.get('zodiac_sign', '')
                    }
                    personality_gates[gate] = planet_data
                    prs_planets.append(planet_data)
        # Handle dict format for personality
        else:
            for planet, data in personality_raw.items():
                gate = data.get('gate')
                if gate:
                    planet_data = {
                        'Planet': planet,
                        'Gate': gate,
                        'Line': data.get('line', 1),
                        'Tone': data.get('tone', 1)
                    }
                    personality_gates[gate] = planet_data
                    prs_planets.append(planet_data)

        return design_gates, personality_gates, des_planets, prs_planets

    return {}, {}, [], []


def svg_to_mpl_path(svg_d):
    """Converts an SVG path string to a Matplotlib Path object."""
    if not svg_d:
        return None
    return parse_path(svg_d)


def get_center_colors(center_name, is_defined, dark_mode=False):
    """Get fill, stroke, and glow colors for a center."""
    if is_defined:
        # Use vibrant dark mode colors or traditional light mode colors
        color_set = DARK_CENTER_COLORS if dark_mode else CENTER_COLORS
        colors = color_set.get(center_name, color_set["G"])
        return colors["defined"], colors["stroke"], colors.get("glow")

    if dark_mode:
        return DARK_UNDEFINED_CENTER["fill"], DARK_UNDEFINED_CENTER["stroke"], DARK_UNDEFINED_CENTER["glow"]
    return UNDEFINED_CENTER["fill"], UNDEFINED_CENTER["stroke"], UNDEFINED_CENTER["glow"]


def draw_glow_effect(ax, x, y, radius, color, layers=4, transform=None):
    """Draw a soft glow effect using layered circles with decreasing opacity."""
    if not color:
        return

    for i in range(layers, 0, -1):
        layer_radius = radius * (1 + i * 0.35)
        alpha = 0.15 / i
        glow_circle = Circle(
            (x, y),
            radius=layer_radius,
            facecolor=color,
            edgecolor='none',
            alpha=alpha,
            zorder=5,
            transform=transform
        )
        ax.add_patch(glow_circle)


def draw_rect_glow(ax, x, y, w, h, color, layers=3, offset_x=0):
    """Draw glow effect for rectangular centers."""
    if not color:
        return

    for i in range(layers, 0, -1):
        expand = i * 3
        alpha = 0.12 / i
        glow_rect = FancyBboxPatch(
            (x - expand + offset_x, y - expand),
            w + expand * 2,
            h + expand * 2,
            boxstyle="round,pad=0,rounding_size=4",
            facecolor=color,
            edgecolor='none',
            alpha=alpha,
            zorder=5
        )
        ax.add_patch(glow_rect)


def draw_background_gradient(ax, width, height, dark_mode=False):
    """Draw a subtle gradient background."""
    # Create gradient using imshow
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack([gradient] * 256)

    # Define colormap from light to slightly darker
    if dark_mode:
        cmap = LinearSegmentedColormap.from_list('bg', [DARK_BG_GRADIENT_START, DARK_BG_GRADIENT_END])
    else:
        cmap = LinearSegmentedColormap.from_list('bg', [COLOR_BG_GRADIENT_START, COLOR_BG_GRADIENT_END])

    ax.imshow(
        gradient.T,
        aspect='auto',
        cmap=cmap,
        extent=[0, width, height, 0],
        zorder=-10,
        alpha=0.5
    )


def draw_body_outline(ax, layout_data, offset_x=0, dark_mode=False):
    """Draw the ethereal body silhouette with ambient glow."""
    body_d = layout_data.get('body_outline', "")
    if not body_d:
        return

    path = svg_to_mpl_path(body_d)
    transform = matplotlib.transforms.Affine2D().translate(offset_x, 0) + ax.transData

    # Ambient ethereal glow - adapted for light/dark mode
    if dark_mode:
        glow_color = DARK_BODY_GLOW_1
        inner_glow_color = DARK_BODY_GLOW_2
        body_bg = DARK_BODY_BG
        body_stroke = DARK_BODY_STROKE
    else:
        glow_color = '#B8C5D6'  # Soft blue-gray
        inner_glow_color = '#D4DCE8'
        body_bg = COLOR_BODY_BG
        body_stroke = COLOR_BODY_STROKE

    for i in range(6, 0, -1):
        glow_patch = PathPatch(
            path,
            facecolor='none',
            edgecolor=glow_color,
            linewidth=2 + i * 3,
            alpha=0.04,
            zorder=-2,
            transform=transform
        )
        ax.add_patch(glow_patch)

    # Inner glow - slightly warmer
    for i in range(3, 0, -1):
        glow_patch = PathPatch(
            path,
            facecolor='none',
            edgecolor=inner_glow_color,
            linewidth=1 + i * 1.5,
            alpha=0.08,
            zorder=-1,
            transform=transform
        )
        ax.add_patch(glow_patch)

    # Main body fill with soft edge
    patch = PathPatch(
        path,
        facecolor=body_bg,
        edgecolor=body_stroke,
        linewidth=1.2,
        alpha=0.9,
        zorder=0,
        transform=transform
    )
    ax.add_patch(patch)


def draw_channels(ax, chart_data, layout_data, offset_x=0, dark_mode=False):
    """Draw channels with luminous effects for active ones."""
    design_gates, personality_gates, _, _ = normalize_gates_data(chart_data)
    channels_layout = layout_data.get('channels', {})

    transform = matplotlib.transforms.Affine2D().translate(offset_x, 0) + ax.transData

    # Select colors based on mode
    channel_inactive = DARK_CHANNEL_INACTIVE if dark_mode else COLOR_CHANNEL_INACTIVE
    channel_glow = DARK_CHANNEL_GLOW if dark_mode else COLOR_CHANNEL_GLOW

    # Activation colors match panel text colors
    design_color = DARK_DESIGN_TEXT if dark_mode else COLOR_DESIGN
    personality_color = DARK_PERSONALITY_TEXT if dark_mode else COLOR_PERSONALITY

    for gate_id_str, geo_data in channels_layout.items():
        gate_id = int(gate_id_str)
        path_d = geo_data.get('channel_path')
        if not path_d:
            continue

        mpl_path = svg_to_mpl_path(path_d)

        # Inactive/undefined channel (visible but muted)
        patch_bg = PathPatch(
            mpl_path,
            facecolor='none',
            edgecolor=channel_inactive,
            linewidth=3.0,
            capstyle='round',
            alpha=0.85,
            zorder=0.5,
            transform=transform
        )
        ax.add_patch(patch_bg)

        is_design = gate_id in design_gates
        is_personality = gate_id in personality_gates

        if not (is_design or is_personality):
            continue

        # Draw glow for active channels
        glow_patch = PathPatch(
            mpl_path,
            facecolor='none',
            edgecolor=channel_glow,
            linewidth=6,
            capstyle='round',
            alpha=0.3,
            zorder=0.8,
            transform=transform
        )
        ax.add_patch(glow_patch)

        if is_design and is_personality:
            # Both - striped pattern
            patch_red = PathPatch(
                mpl_path,
                facecolor='none',
                edgecolor=design_color,
                linewidth=3.5,
                capstyle='round',
                zorder=1,
                transform=transform
            )
            ax.add_patch(patch_red)
            patch_blk = PathPatch(
                mpl_path,
                facecolor='none',
                edgecolor=personality_color,
                linewidth=3.5,
                linestyle=(0, (0.5, 2)),  # Tiny frequent dashes - visible striping pattern
                capstyle='round',
                zorder=1.1,
                transform=transform
            )
            ax.add_patch(patch_blk)
        elif is_design:
            patch = PathPatch(
                mpl_path,
                facecolor='none',
                edgecolor=design_color,
                linewidth=3.5,
                capstyle='round',
                zorder=1,
                transform=transform
            )
            ax.add_patch(patch)
        else:
            patch = PathPatch(
                mpl_path,
                facecolor='none',
                edgecolor=personality_color,
                linewidth=3.5,
                capstyle='round',
                zorder=1,
                transform=transform
            )
            ax.add_patch(patch)


def draw_centers(ax, chart_data, layout_data, offset_x=0, dark_mode=False):
    """Draw centers with luminous glow effects."""
    defined_centers = set(chart_data['general'].get('defined_centers', []))

    if "Anja" in defined_centers:
        defined_centers.remove("Anja")
        defined_centers.add("Ajna")

    centers_layout = layout_data.get('centers', {})

    for name, data in centers_layout.items():
        json_name = name if name != "G" else "G_Center"
        is_defined = json_name in defined_centers or name in defined_centers
        fill_c, stroke_c, glow_c = get_center_colors(name, is_defined, dark_mode)

        stroke_width = 2.0 if is_defined else 1.2

        if data['type'] == 'rect':
            x, y, w, h = data['x'], data['y'], data['w'], data['h']

            # Center glow removed for cleaner appearance
            # (defined centers distinguished by fill color alone)

            rect = FancyBboxPatch(
                (x + offset_x, y),
                w, h,
                boxstyle="round,pad=0,rounding_size=2",
                linewidth=stroke_width,
                edgecolor=stroke_c,
                facecolor=fill_c,
                zorder=10
            )
            ax.add_patch(rect)

        elif data['type'] == 'path':
            path = svg_to_mpl_path(data['path'])

            transform_str = data.get('transform')
            if transform_str:
                t_vals = [float(v) for v in transform_str.split()]
                if len(t_vals) == 6:
                    base_t = matplotlib.transforms.Affine2D.from_values(*t_vals)
                    combined_t = base_t + matplotlib.transforms.Affine2D().translate(offset_x, 0) + ax.transData
                else:
                    combined_t = matplotlib.transforms.Affine2D().translate(offset_x, 0) + ax.transData
            else:
                combined_t = matplotlib.transforms.Affine2D().translate(offset_x, 0) + ax.transData

            # Center glow removed for cleaner appearance

            patch = PathPatch(
                path,
                facecolor=fill_c,
                edgecolor=stroke_c,
                linewidth=stroke_width,
                zorder=10,
                transform=combined_t
            )
            ax.add_patch(patch)


def get_gate_center(gate_id):
    """Get the center name for a given gate."""
    from ..hd_constants import GATES_CHAKRA_DICT, CHAKRA_NAMES_MAP

    for (g1, g2), (c1, c2) in GATES_CHAKRA_DICT.items():
        if gate_id == g1:
            return CHAKRA_NAMES_MAP.get(c1, "G")
        if gate_id == g2:
            return CHAKRA_NAMES_MAP.get(c2, "G")
    return "G"


def draw_gate_numbers(ax, chart_data, layout_data, offset_x=0, dark_mode=False):
    """Draw gate numbers with split-aspect activation border indicators."""
    font = get_font()
    gate_coords = layout_data.get('gates_coords', {})
    design_gates, personality_gates, _, _ = normalize_gates_data(chart_data)
    defined_centers = set(chart_data['general'].get('defined_centers', []))

    if "Anja" in defined_centers:
        defined_centers.remove("Anja")
        defined_centers.add("Ajna")

    # Activation colors match panel text colors
    design_color = DARK_DESIGN_TEXT if dark_mode else COLOR_DESIGN
    personality_color = DARK_PERSONALITY_TEXT if dark_mode else COLOR_PERSONALITY

    for gate_id_str, pt in gate_coords.items():
        gate_id = int(gate_id_str)
        x, y = pt['x'] + offset_x, pt['y']

        is_design = gate_id in design_gates
        is_personality = gate_id in personality_gates
        is_active = is_design or is_personality

        center_x = x + 3.25
        center_y = y + 3.25
        radius = 4.2 if is_active else 2.8

        if is_active:
            center_name = get_gate_center(gate_id)
            json_center_name = center_name if center_name != "G" else "G_Center"
            is_center_defined = json_center_name in defined_centers or center_name in defined_centers

            _, stroke_color, glow_color = get_center_colors(center_name, is_center_defined, dark_mode)

            if not is_center_defined:
                stroke_color = "#9B59B6"
                glow_color = "#E8D5F2"

            # Center-colored glow (subtle)
            if glow_color:
                glow = Circle(
                    (center_x, center_y),
                    radius=radius + 2,
                    facecolor=glow_color,
                    edgecolor='none',
                    alpha=0.4,
                    zorder=18
                )
                ax.add_patch(glow)

            # Gate circle (white background, no border yet)
            circ = Circle(
                (center_x, center_y),
                radius=radius,
                facecolor='white',
                edgecolor='none',
                linewidth=0,
                zorder=20
            )
            ax.add_patch(circ)

            # Activation-based border: split design/personality for both aspects, full color for single aspect
            if is_design and is_personality:
                # Both aspects: half design (left), half personality (right)
                from matplotlib.patches import Arc

                arc_design = Arc(
                    (center_x, center_y),
                    radius * 2, radius * 2,
                    angle=0,
                    theta1=90,  # Start at top
                    theta2=270,  # End at bottom (left half)
                    color=design_color,
                    linewidth=2.0,
                    zorder=21
                )
                ax.add_patch(arc_design)

                arc_personality = Arc(
                    (center_x, center_y),
                    radius * 2, radius * 2,
                    angle=0,
                    theta1=270,  # Start at bottom
                    theta2=450,  # End at top (right half)
                    color=personality_color,
                    linewidth=2.0,
                    zorder=21
                )
                ax.add_patch(arc_personality)

            elif is_design:
                # Design only: full border
                border = Circle(
                    (center_x, center_y),
                    radius=radius,
                    facecolor='none',
                    edgecolor=design_color,
                    linewidth=2.0,
                    zorder=21
                )
                ax.add_patch(border)

            elif is_personality:
                # Personality only: full border
                border = Circle(
                    (center_x, center_y),
                    radius=radius,
                    facecolor='none',
                    edgecolor=personality_color,
                    linewidth=2.0,
                    zorder=21
                )
                ax.add_patch(border)

        fontsize = 5.8 if is_active else 4.2
        fontweight = 'bold' if is_active else 'normal'

        # Gate number color
        if is_active:
            # Active gates have white circles - use black text for contrast (both modes)
            color = '#1A1A1A'
        else:
            # Inactive gates - adapt for dark mode background
            color = DARK_GATE_INACTIVE_COLOR if dark_mode else '#7F8C8D'

        ax.text(
            center_x, center_y,
            str(gate_id),
            fontsize=fontsize,
            fontweight=fontweight,
            ha='center',
            va='center',
            zorder=22,
            color=color,
            fontfamily=font
        )


def load_alchemical_symbol_path(symbol_name):
    """Load alchemical symbol SVG and extract path data for vector rendering."""
    try:
        # Path to symbol SVG file (in Cartographer root folder)
        svg_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', f'{symbol_name}.svg')

        # Parse SVG
        tree = ET.parse(svg_path)
        root = tree.getroot()

        # Get viewBox dimensions for scaling
        viewbox = root.get('viewBox', '0 0 400 400')
        vb_parts = viewbox.split()
        vb_width = float(vb_parts[2]) if len(vb_parts) > 2 else 400
        vb_height = float(vb_parts[3]) if len(vb_parts) > 3 else 400

        # Find path element
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        path_elem = root.find('.//svg:path', ns)
        if path_elem is None:
            path_elem = root.find('.//path')

        if path_elem is not None:
            path_data = path_elem.get('d')
            if path_data:
                # Parse SVG path to matplotlib path
                mpl_path = parse_path(path_data)
                return mpl_path, vb_width, vb_height

    except Exception as e:
        print(f"Warning: Could not load {symbol_name}.svg: {e}")
    return None, None, None


def draw_planetary_panel(ax, planets_data, x_start, is_design=True, panel_width=PANEL_WIDTH, variables=None, exaltations=None, opposite_planets_data=None, channels=None, dark_mode=False):
    """Draw an elegant side panel with planetary activations (Neutrino Design style)."""
    font = get_font()
    symbol_font = get_symbol_font()
    variables = variables or {}
    exaltations = exaltations or {}
    opposite_planets_data = opposite_planets_data or []
    channels = channels or []

    # Build channel map: gate -> opposite_gate
    channel_map = {}
    for channel_info in channels:
        if isinstance(channel_info, dict):
            channel = channel_info.get('channel', '')
        else:
            channel = str(channel_info)

        # Extract gate numbers (e.g., "6/59" or "6-59")
        channel = channel.split(':')[0].strip()
        if '/' in channel:
            parts = channel.split('/')
        elif '-' in channel:
            parts = channel.split('-')
        else:
            continue

        if len(parts) == 2:
            try:
                g1, g2 = int(parts[0].strip()), int(parts[1].strip())
                channel_map[g1] = g2
                channel_map[g2] = g1
            except ValueError:
                pass

    # Build opposite planet lookup: gate -> planet_name
    opposite_planet_lookup = {p.get('Gate'): p.get('Planet') for p in opposite_planets_data if p.get('Gate')}

    # Build gate-level planet map: gate -> list of all planets at that gate (any line, both aspects)
    gate_planet_map = {}
    for planet_data in planets_data:
        gate = planet_data.get('Gate')
        planet = planet_data.get('Planet')
        if gate and planet:
            if gate not in gate_planet_map:
                gate_planet_map[gate] = []
            gate_planet_map[gate].append(planet)

    for planet_data in opposite_planets_data:
        gate = planet_data.get('Gate')
        planet = planet_data.get('Planet')
        if gate and planet:
            if gate not in gate_planet_map:
                gate_planet_map[gate] = []
            gate_planet_map[gate].append(planet)

    # Layout constants
    header_height = 26  # Increased from 22 for better hierarchy
    cell_height = 21
    num_planets = len(PLANET_ORDER)
    panel_top = 8
    panel_height = header_height + (num_planets * cell_height) + 4

    # Magenta/Electric Blue color scheme matching gate activations (with dark mode support)
    if dark_mode:
        if is_design:
            # Design Panel (dark mode): Luminous magenta palette
            panel_color = '#2A182A'      # Deep magenta tint background
            panel_border = '#DD44BB'     # Vibrant magenta border (matches activations)
            cell_border = '#442244'      # Subtle magenta divider
            header_border = '#DD44BB'    # Vibrant magenta
            row_alt_color = '#321E32'    # Alternating row tint (magenta)
            header_color = DARK_DESIGN_HEADER  # Bright magenta
            text_color = DARK_DESIGN_TEXT      # Pure magenta
        else:
            # Personality Panel (dark mode): Luminous electric blue palette
            panel_color = '#1A2035'      # Deep blue tint background
            panel_border = '#5588DD'     # Electric blue border (matches activations)
            cell_border = '#2A3550'      # Subtle blue divider
            header_border = '#5588DD'    # Electric blue
            row_alt_color = '#1F2840'    # Alternating row tint (blue)
            header_color = DARK_PERSONALITY_HEADER  # Bright electric blue
            text_color = DARK_PERSONALITY_TEXT      # Electric blue
    else:
        if is_design:
            # Design Panel (light mode): Red palette (matches red gate activations)
            panel_color = '#FFF5F5'      # Very light red/pink
            panel_border = '#C45555'     # Muted red
            cell_border = '#E8B8B8'      # Subtle red divider
            header_border = '#A03030'    # Deep red
            row_alt_color = '#FFF0F0'    # Alternating row tint (subtle red)
            header_color = COLOR_DESIGN
            text_color = COLOR_DESIGN
        else:
            # Personality Panel (light mode): Black/grey palette (matches black gate activations)
            panel_color = '#F8F8F8'      # Very light grey
            panel_border = '#606060'     # Medium grey
            cell_border = '#D0D0D0'      # Subtle grey divider
            header_border = '#303030'    # Deep grey/black
            row_alt_color = '#F0F0F0'    # Alternating row tint (subtle grey)
            header_color = COLOR_PERSONALITY
            text_color = COLOR_PERSONALITY

    # Panel outer border with stronger definition
    border_width = 2.5 if dark_mode else 2.0  # Slightly thicker in dark mode
    outer_rect = FancyBboxPatch(
        (x_start + 2, panel_top),
        panel_width - 4,
        panel_height,
        boxstyle="round,pad=0.02,rounding_size=4",
        facecolor=panel_color,
        edgecolor=panel_border,
        linewidth=border_width,
        zorder=1
    )
    ax.add_patch(outer_rect)

    # Alchemical symbol header (from vector SVG files)
    # Salt = Design/Body/Fixed principle
    # Sulphur = Personality/Soul/Active principle
    symbol_name = 'salt' if is_design else 'sulphur'
    symbol_path, vb_width, vb_height = load_alchemical_symbol_path(symbol_name)

    # Accent color for separator (use vibrant border color in dark mode)
    accent_color = panel_border

    # Header text
    if is_design:
        header_text = "Design"
    else:
        header_text = "Personality"

    # Position in header area
    header_y = panel_top + (header_height / 2) + 3
    header_center_x = x_start + panel_width / 2

    # Simple centered rendering with font fallback
    ax.text(
        header_center_x,
        header_y,
        header_text,
        fontsize=12,
        fontweight='bold',
        ha='center',
        va='center',
        color=header_color,
        fontfamily=[font, 'Noto Sans Symbols'],
        alpha=0.9,
        zorder=3
    )

    header_text_y = header_y + 8  # Position separator below header elements

    # Vibrant separator line below header
    separator_y = header_text_y + 3  # 3 pixels below symbol/text
    separator_alpha = 0.9 if dark_mode else 0.7  # More vibrant in dark mode
    ax.plot(
        [x_start + 8, x_start + panel_width - 8],  # Inset from edges
        [separator_y, separator_y],
        color=accent_color,  # Vibrant border color
        linewidth=1.5,
        alpha=separator_alpha,
        solid_capstyle='round',
        zorder=2
    )

    # Draw cell dividers and planet rows (below the header)
    planet_lookup = {p['Planet']: p for p in planets_data}
    cells_start_y = panel_top + header_height + 2  # Start right below header

    # Calculate triangle x position ONCE for the entire panel
    # Panel visible area: x_start + 2 (left border) to x_start + panel_width - 2 (right border)
    planet_gate_spacing = 16  # Consistent spacing between planet and gate on both sides

    if is_design:
        # Design: planet → gate.line → triangle (triangle on RIGHT, toward body)
        planet_x = x_start + 8
        gate_x = planet_x + planet_gate_spacing - 1  # 1px to the left
        # Triangle positioned 10px from visible right border
        # Visible right border is at: x_start + panel_width - 2
        triangle_x = x_start + panel_width - 2 - 10
    else:
        # Personality: triangle → gate.line → planet (triangle on LEFT, toward body)
        planet_x = x_start + panel_width - 8  # Planet on right
        gate_x = planet_x - planet_gate_spacing + 1  # 1px to the right
        # Triangle positioned 10px from visible left border
        # Visible left border is at: x_start + 2
        triangle_x = x_start + 2 + 10

    for i, planet_name in enumerate(PLANET_ORDER):
        cell_top_y = cells_start_y + (i * cell_height)
        text_y = cell_top_y + cell_height / 2  # Center text vertically in cell

        # Alternating row background (zebra striping for better scanning)
        if i % 2 == 0:  # Every other row
            alt_row_rect = FancyBboxPatch(
                (x_start + 3, cell_top_y),
                panel_width - 6,
                cell_height,
                boxstyle="square,pad=0",
                facecolor=row_alt_color,
                edgecolor='none',
                alpha=0.5,  # Subtle tint
                zorder=1.5
            )
            ax.add_patch(alt_row_rect)

        # Draw cell border (horizontal line at top of each cell, skip first)
        if i > 0:
            ax.plot(
                [x_start + 4, x_start + panel_width - 4],
                [cell_top_y, cell_top_y],
                color=cell_border,
                linewidth=0.8,
                alpha=0.6,  # Slightly transparent for subtlety
                zorder=2
            )

        planet_data = planet_lookup.get(planet_name, {})
        gate = planet_data.get('Gate', '–')
        line = planet_data.get('Line', '–')
        tone = planet_data.get('Tone', 0)

        symbol = PLANET_SYMBOLS.get(planet_name, "?")

        # Planet symbol (monospace font ensures consistent alignment)
        ax.text(
            planet_x,
            text_y + 0.5,  # Aligned with gate text
            symbol,
            fontsize=16,
            ha='left' if is_design else 'right',
            va='center',
            color=text_color,
            fontfamily=symbol_font,
            zorder=3
        )

        # Gate.Line (larger, bolder - matching Neutrino Design)
        gate_line_text = f"{gate}.{line}"
        gate_text_y = text_y + 0.5  # Slight upward adjustment for better visual centering
        ax.text(
            gate_x,
            gate_text_y,
            gate_line_text,
            fontsize=11,
            ha='left' if is_design else 'right',
            va='center',
            color=text_color,
            fontfamily=font,
            fontweight='bold',
            zorder=3
        )

        # Variables arrows for Sun and North_Node (left/right - the "Four Transformations")
        arrow = None

        if planet_name == 'Sun':
            # Sun arrow from Variables: Design=top_left (Digestion), Personality=top_right (Motivation)
            var_key = 'top_left' if is_design else 'top_right'
            var_data = variables.get(var_key, {})
            direction = var_data.get('value', '') if isinstance(var_data, dict) else var_data
            if direction == 'left':
                arrow = '←'
            elif direction == 'right':
                arrow = '→'
        elif planet_name == 'North_Node':
            # Node arrow from Variables: Design=bottom_left (Environment), Personality=bottom_right (Perspective)
            var_key = 'bottom_left' if is_design else 'bottom_right'
            var_data = variables.get(var_key, {})
            direction = var_data.get('value', '') if isinstance(var_data, dict) else var_data
            if direction == 'left':
                arrow = '←'
            elif direction == 'right':
                arrow = '→'

        # Read dignity from planet data (already calculated by get_hd_data.py)
        dignity = planet_data.get('dignity')
        # Render dignity symbol (triangle or star) - centered in cell
        if dignity == 'juxtaposed':
            # Draw four-pointed star for juxtaposition
            ax.text(
                triangle_x,
                text_y,  # Use text_y for true cell center (not gate_text_y)
                '✦',  # U+2726 BLACK FOUR POINTED STAR
                fontsize=12,  # 20% larger (was 10)
                ha='center',
                va='center',
                color=text_color,
                zorder=3
            )
        elif dignity:
            # Render text symbol for exalted (▲) or detriment (▽)
            symbol = '▲' if dignity == 'exalted' else '▽'  # U+25BD WHITE DOWN-POINTING TRIANGLE
            ax.text(
                triangle_x,
                text_y,  # Use text_y for true cell center (not gate_text_y)
                symbol,
                fontsize=10,  # 20% larger (was 8)
                ha='center',
                va='center',
                color=text_color,
                zorder=3
            )

        # Draw Variables arrows (left/right) for Sun and Nodes
        # OUTSIDE the panel borders, on the side closest to the body
        if arrow:
            if is_design:
                # Design arrows: to the RIGHT of the panel (toward body)
                arrow_x = x_start + panel_width + 12
            else:
                # Personality arrows: to the LEFT of the panel (toward body)
                arrow_x = x_start - 12

            ax.text(
                arrow_x,
                gate_text_y,  # Aligned with gate text and triangles
                arrow,
                fontsize=16,  # Increased for better visibility
                ha='center',
                va='center',
                color=text_color,
                alpha=1.0,
                zorder=3
            )


def draw_summary_panel(ax, chart_data, canvas_width, y_start):
    """Draw an elegant bottom summary panel."""
    font = get_font()
    general = chart_data.get('general', {})

    # Panel background - spans ~95% of canvas width
    margin = canvas_width * 0.025  # 2.5% margin on each side
    rect = FancyBboxPatch(
        (margin, y_start + 5),
        canvas_width - (margin * 2),
        SUMMARY_HEIGHT - 10,
        boxstyle="round,pad=0.02,rounding_size=6",
        facecolor='#FAFBFC',
        edgecolor='#E8EBED',
        linewidth=1.5,
        zorder=15
    )
    ax.add_patch(rect)

    # Extract data
    energy_type = general.get('energy_type', 'Unknown')
    strategy = general.get('strategy', 'Unknown')
    authority = general.get('inner_authority', 'Unknown')
    profile = general.get('profile', 'Unknown')
    inc_cross = general.get('inc_cross', 'Unknown')
    definition = general.get('definition', 'Unknown')

    # Variables - extract left/right orientation for the 4 arrows
    # Format: P[Motivation L/R][Perspective L/R] D[Digestion L/R][Environment L/R]
    # Example: PLLDRL = Personality Left-Left, Design Right-Left
    # Handles both nested format {"top_left": {"value": "left"}} and flat format {"top_left": "left"}
    variables = general.get('variables', {})
    var_string = ""
    if variables:
        def get_var_direction(key):
            val = variables.get(key, {})
            if isinstance(val, dict):
                return val.get('value', 'right')
            return val if val in ('left', 'right') else 'right'

        # Arrow positions:
        # top_left = Design Sun/Earth (Digestion/Determination)
        # bottom_left = Design Nodes (Environment)
        # top_right = Personality Sun/Earth (Motivation/Awareness)
        # bottom_right = Personality Nodes (Perspective/View)

        motivation = "L" if get_var_direction('top_right') == 'left' else "R"
        perspective = "L" if get_var_direction('bottom_right') == 'left' else "R"
        digestion = "L" if get_var_direction('top_left') == 'left' else "R"
        environment = "L" if get_var_direction('bottom_left') == 'left' else "R"

        var_string = f"P{motivation}{perspective}D{digestion}{environment}"

    # Layout for summary panel - compact spacing
    col_width = (canvas_width - 40) / 3
    x_start = 25  # Left margin for content
    y_row1 = y_start + 35
    y_row2 = y_start + 80

    label_color = '#7F8C8D'
    value_color = '#2C3E50'

    def draw_info(x, y, label, value, small=False):
        # Text needs higher zorder than panel background (15)
        ax.text(x, y - 10, label, fontsize=9, color=label_color, fontweight='bold', fontfamily=font, zorder=20)
        fs = 11 if small else 13
        ax.text(x, y + 10, str(value), fontsize=fs, color=value_color, fontweight='bold', fontfamily=font, zorder=20)

    # Row 1: Type, Strategy, Authority
    draw_info(x_start, y_row1, "TYPE", energy_type)
    draw_info(x_start + col_width, y_row1, "STRATEGY", strategy)
    draw_info(x_start + col_width * 2, y_row1, "AUTHORITY", authority)

    # Row 2: Profile, Definition, Cross
    draw_info(x_start, y_row2, "PROFILE", profile)
    draw_info(x_start + col_width, y_row2, "DEFINITION", definition)

    # Incarnation Cross (shortened)
    cross_short = inc_cross
    if len(inc_cross) > 30:
        cross_short = inc_cross.replace("The Right Angle Cross of ", "RAC ")
        cross_short = cross_short.replace("The Left Angle Cross of ", "LAC ")
        cross_short = cross_short.replace("The Juxtaposition Cross of ", "JC ")

    draw_info(x_start + col_width * 2, y_row2, "CROSS", cross_short, small=True)

    # Variables badge with label (6-character format: PLLDRL)
    if var_string:
        badge_x = canvas_width - 55
        badge_y = y_start + 35

        # Label above badge
        ax.text(badge_x + 26, badge_y - 16, "VARIABLES", fontsize=9, color=label_color,
                fontweight='bold', ha='center', va='center', fontfamily=font, zorder=20)

        # Badge background
        badge = FancyBboxPatch(
            (badge_x - 2, badge_y - 8),
            58, 24,
            boxstyle="round,pad=0.02,rounding_size=4",
            facecolor='#EBF5FB',
            edgecolor='#85C1E9',
            linewidth=1,
            zorder=16
        )
        ax.add_patch(badge)

        # Variable string
        ax.text(badge_x + 27, badge_y + 4, var_string, fontsize=11, color='#2980B9',
                fontweight='bold', ha='center', va='center', fontfamily='monospace', zorder=20)


def draw_chart(chart_data, layout_data, include_panels=True, include_summary=True, dark_mode=False):
    """
    Main chart drawing function with luminous/ethereal style.

    Args:
        chart_data: Chart data dictionary
        layout_data: Layout geometry data
        include_panels: Whether to include planetary panels
        include_summary: Whether to include summary panel
        dark_mode: Whether to use dark mode colors
    """
    # Ensure chart data has all necessary fields (derive defined_centers, strategy, etc.)
    chart_data = ensure_chart_data_complete(chart_data)

    # Calculate canvas dimensions
    if include_panels:
        canvas_w = BODYGRAPH_W + (PANEL_WIDTH * 2)
        # Centering correction: bodygraph geometry is slightly left of center in layout_data
        bodygraph_offset_x = PANEL_WIDTH + 2.75
    else:
        canvas_w = BODYGRAPH_W
        bodygraph_offset_x = 0

    canvas_h = BODYGRAPH_H + SUMMARY_HEIGHT if include_summary else BODYGRAPH_H

    # Figure setup
    aspect = canvas_h / canvas_w
    fig_width = 10
    fig_height = fig_width * aspect

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=150)
    ax.set_xlim(0, canvas_w)
    ax.set_ylim(canvas_h, 0)
    ax.axis('off')

    # Background - dark gray for dark mode (matches macOS dark appearance)
    bg_color = '#1e1e1e' if dark_mode else 'white'
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Side panels
    if include_panels:
        _, _, design_planets, personality_planets = normalize_gates_data(chart_data)
        variables = chart_data.get('general', {}).get('variables', {})
        exaltations = load_exaltations_data()
        channels = chart_data.get('channels', {}).get('Channels', [])

        # Draw Design panel (with Personality as opposite for harmonic fixing)
        draw_planetary_panel(ax, design_planets, 0, is_design=True,
                           variables=variables, exaltations=exaltations,
                           opposite_planets_data=personality_planets, channels=channels,
                           dark_mode=dark_mode)

        # Draw Personality panel (with Design as opposite for harmonic fixing)
        draw_planetary_panel(ax, personality_planets, canvas_w - PANEL_WIDTH, is_design=False,
                           variables=variables, exaltations=exaltations,
                           opposite_planets_data=design_planets, channels=channels,
                           dark_mode=dark_mode)

    # Body silhouette
    draw_body_outline(ax, layout_data, bodygraph_offset_x, dark_mode=dark_mode)

    # Channels
    draw_channels(ax, chart_data, layout_data, bodygraph_offset_x, dark_mode=dark_mode)

    # Centers with glow
    draw_centers(ax, chart_data, layout_data, bodygraph_offset_x, dark_mode=dark_mode)

    # Gate numbers
    draw_gate_numbers(ax, chart_data, layout_data, bodygraph_offset_x, dark_mode=dark_mode)

    # Summary panel
    if include_summary:
        draw_summary_panel(ax, chart_data, canvas_w, BODYGRAPH_H)

    return fig


def generate_bodygraph_image(chart_data, fmt='png', include_panels=True, include_summary=False, dark_mode=False):
    """
    Generates the BodyGraph image and returns it as bytes.

    Args:
        chart_data: Chart data dictionary
        fmt: Output format ('png', 'svg', 'jpg')
        include_panels: Whether to include planetary panels
        include_summary: Whether to include summary panel
        dark_mode: Whether to use dark mode colors
    """
    layout = load_json_layout()
    fig = draw_chart(chart_data, layout, include_panels=include_panels, include_summary=include_summary, dark_mode=dark_mode)

    buf = io.BytesIO()

    # PNG supports transparency; JPEG does not
    if fmt.lower() in ['jpg', 'jpeg']:
        fig.patch.set_facecolor('white')
        ax = fig.axes[0]
        ax.set_facecolor('white')
        transparent = False
    else:
        transparent = True

    fig.savefig(buf, format=fmt, bbox_inches='tight', pad_inches=0.1,
                transparent=transparent)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# --- Standalone testing ---
if __name__ == "__main__":
    test_data = """
{
  "general": {
    "birth_date": "1968-02-21 11:00",
    "energy_type": "Manifesting Generator",
    "strategy": "Wait to Respond",
    "inner_authority": "Solar Plexus",
    "inc_cross": "The Right Angle Cross of the Sleeping Phoenix (1)",
    "profile": "2/4: Hermit Opportunist",
    "defined_centers": ["Heart", "Throat", "G_Center", "Root", "Sacral", "SolarPlexus", "Spleen"],
    "undefined_centers": ["Ajna", "Head"],
    "definition": "Single Definition",
    "variables": {"top_right": "right", "bottom_right": "left", "top_left": "right", "bottom_left": "right"}
  },
  "gates": {
    "prs": {
      "Planets": [
        {"Planet": "Sun", "Gate": 55, "Line": 2, "Tone": 3},
        {"Planet": "Earth", "Gate": 59, "Line": 2, "Tone": 3},
        {"Planet": "Moon", "Gate": 34, "Line": 5, "Tone": 2},
        {"Planet": "North_Node", "Gate": 51, "Line": 6, "Tone": 2},
        {"Planet": "South_Node", "Gate": 57, "Line": 6, "Tone": 2},
        {"Planet": "Mercury", "Gate": 49, "Line": 2, "Tone": 2},
        {"Planet": "Venus", "Gate": 60, "Line": 6, "Tone": 1},
        {"Planet": "Mars", "Gate": 25, "Line": 6, "Tone": 5},
        {"Planet": "Jupiter", "Gate": 59, "Line": 1, "Tone": 1},
        {"Planet": "Saturn", "Gate": 21, "Line": 1, "Tone": 6},
        {"Planet": "Uranus", "Gate": 6, "Line": 6, "Tone": 6},
        {"Planet": "Neptune", "Gate": 14, "Line": 3, "Tone": 6},
        {"Planet": "Pluto", "Gate": 47, "Line": 6, "Tone": 3}
      ]
    },
    "des": {
      "Planets": [
        {"Planet": "Sun", "Gate": 34, "Line": 4, "Tone": 2},
        {"Planet": "Earth", "Gate": 20, "Line": 4, "Tone": 2},
        {"Planet": "Moon", "Gate": 6, "Line": 4, "Tone": 4},
        {"Planet": "North_Node", "Gate": 3, "Line": 2, "Tone": 4},
        {"Planet": "South_Node", "Gate": 50, "Line": 2, "Tone": 4},
        {"Planet": "Mercury", "Gate": 1, "Line": 4, "Tone": 3},
        {"Planet": "Venus", "Gate": 57, "Line": 4, "Tone": 4},
        {"Planet": "Mars", "Gate": 61, "Line": 6, "Tone": 6},
        {"Planet": "Jupiter", "Gate": 59, "Line": 5, "Tone": 6},
        {"Planet": "Saturn", "Gate": 17, "Line": 3, "Tone": 2},
        {"Planet": "Uranus", "Gate": 46, "Line": 1, "Tone": 5},
        {"Planet": "Neptune", "Gate": 43, "Line": 6, "Tone": 4},
        {"Planet": "Pluto", "Gate": 47, "Line": 6, "Tone": 6}
      ]
    }
  },
  "channels": {"Channels": []}
}
"""

    chart = json.loads(test_data)
    img_bytes = generate_bodygraph_image(chart, fmt='png', include_panels=True, include_summary=True)
    with open("bodygraph_luminous.png", "wb") as f:
        f.write(img_bytes)
    print("Luminous chart saved to bodygraph_luminous.png")
