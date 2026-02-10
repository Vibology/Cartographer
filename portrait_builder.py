#!/usr/bin/env python3
"""
Portrait Chart Builder - Extract essential elements from Kerykeion landscape SVG
and build a clean portrait layout (620×920).

Phase 1: Title, metadata, zodiacal info, moon phase, wheel only.
"""

import re
import sys


def extract_section(svg_content, pattern, flags=re.DOTALL):
    """Extract a section using regex pattern."""
    match = re.search(pattern, svg_content, flags)
    return match.group(1) if match else ''


def apply_color_theme(svg_content, theme='light'):
    """Apply light or dark color theme to the chart.

    Args:
        theme: 'light' (white bg, dark text, for print) or 'dark' (dark bg, light text, for screen)

    Light theme: White background, black text, vibrant zodiac colors
    Dark theme: Dark background, light text, adjusted colors for dark viewing
    """
    if theme == 'dark':
        # Dark mode color palette
        color_map = {
            # Paper colors (background and text)
            '--kerykeion-chart-color-paper-0: #000000': '--kerykeion-chart-color-paper-0: #e8e8e8',  # Text: black → light gray
            '--kerykeion-chart-color-paper-1: #ffffff': '--kerykeion-chart-color-paper-1: #0d0d0d',  # Background: white → very dark gray

            # Fire signs - brighter, more saturated for dark mode
            '--kerykeion-chart-color-zodiac-bg-0: #ff4500': '--kerykeion-chart-color-zodiac-bg-0: #ff6633',  # Aries - brighter red-orange
            '--kerykeion-chart-color-zodiac-bg-4: #ff6b35': '--kerykeion-chart-color-zodiac-bg-4: #ff7d4d',  # Leo - brighter coral
            '--kerykeion-chart-color-zodiac-bg-8: #ff8c42': '--kerykeion-chart-color-zodiac-bg-8: #ffa060',  # Sag - brighter orange

            # Earth signs - lighter, more visible on dark
            '--kerykeion-chart-color-zodiac-bg-1: #6b8e23': '--kerykeion-chart-color-zodiac-bg-1: #8bad3a',  # Taurus - lighter olive
            '--kerykeion-chart-color-zodiac-bg-5: #8b7355': '--kerykeion-chart-color-zodiac-bg-5: #a68968',  # Virgo - lighter brown
            '--kerykeion-chart-color-zodiac-bg-9: #556b2f': '--kerykeion-chart-color-zodiac-bg-9: #6d8a3d',  # Cap - lighter olive

            # Air signs - brighter blues/purples
            '--kerykeion-chart-color-zodiac-bg-2: #4682b4': '--kerykeion-chart-color-zodiac-bg-2: #5c9fd4',  # Gemini - brighter steel blue
            '--kerykeion-chart-color-zodiac-bg-6: #6a5acd': '--kerykeion-chart-color-zodiac-bg-6: #8674e0',  # Libra - brighter slate blue
            '--kerykeion-chart-color-zodiac-bg-10: #5f9ea0': '--kerykeion-chart-color-zodiac-bg-10: #7ab8bb', # Aquarius - brighter cadet blue

            # Water signs - lighter, more luminous
            '--kerykeion-chart-color-zodiac-bg-3: #20b2aa': '--kerykeion-chart-color-zodiac-bg-3: #3dd4cc',  # Cancer - brighter sea green
            '--kerykeion-chart-color-zodiac-bg-7: #483d8b': '--kerykeion-chart-color-zodiac-bg-7: #6052ad',  # Scorpio - brighter slate blue
            '--kerykeion-chart-color-zodiac-bg-11: #4169e1': '--kerykeion-chart-color-zodiac-bg-11: #5b85ff', # Pisces - brighter royal blue

            # Zodiac symbol/icon colors - optimized for dark background readability
            # Fire signs (Aries, Leo, Sagittarius) - icons 0, 4, 8
            '--kerykeion-chart-color-zodiac-icon-0: #ff7200': '--kerykeion-chart-color-zodiac-icon-0: #ff9933',   # Fire - bright orange
            '--kerykeion-chart-color-zodiac-icon-4: #ff7200': '--kerykeion-chart-color-zodiac-icon-4: #ff9933',   # Fire - bright orange
            '--kerykeion-chart-color-zodiac-icon-8: #ff7200': '--kerykeion-chart-color-zodiac-icon-8: #ff9933',   # Fire - bright orange

            # Earth signs (Taurus, Virgo, Capricorn) - icons 1, 5, 9
            '--kerykeion-chart-color-zodiac-icon-1: #6b3d00': '--kerykeion-chart-color-zodiac-icon-1: #e6d4aa',   # Earth - bright tan/beige
            '--kerykeion-chart-color-zodiac-icon-5: #6b3d00': '--kerykeion-chart-color-zodiac-icon-5: #e6d4aa',   # Earth - bright tan/beige
            '--kerykeion-chart-color-zodiac-icon-9: #6b3d00': '--kerykeion-chart-color-zodiac-icon-9: #e6d4aa',   # Earth - bright tan/beige

            # Air signs (Gemini, Libra, Aquarius) - icons 2, 6, 10
            '--kerykeion-chart-color-zodiac-icon-2: #69acf1': '--kerykeion-chart-color-zodiac-icon-2: #99ccff',   # Air - bright sky blue
            '--kerykeion-chart-color-zodiac-icon-6: #69acf1': '--kerykeion-chart-color-zodiac-icon-6: #99ccff',   # Air - bright sky blue
            '--kerykeion-chart-color-zodiac-icon-10: #69acf1': '--kerykeion-chart-color-zodiac-icon-10: #99ccff', # Air - bright sky blue

            # Water signs (Cancer, Scorpio, Pisces) - icons 3, 7, 11
            '--kerykeion-chart-color-zodiac-icon-3: #2b4972': '--kerykeion-chart-color-zodiac-icon-3: #8cb3ff',   # Water - bright blue
            '--kerykeion-chart-color-zodiac-icon-7: #2b4972': '--kerykeion-chart-color-zodiac-icon-7: #8cb3ff',   # Water - bright blue
            '--kerykeion-chart-color-zodiac-icon-11: #2b4972': '--kerykeion-chart-color-zodiac-icon-11: #8cb3ff', # Water - bright blue

            # Aspect colors - adjusted for dark background visibility
            '--kerykeion-chart-color-conjunction: #5555ff': '--kerykeion-chart-color-conjunction: #7d7dff',    # Brighter blue
            '--kerykeion-chart-color-sextile: #ffa500': '--kerykeion-chart-color-sextile: #ffb933',           # Brighter orange
            '--kerykeion-chart-color-square: #ff0000': '--kerykeion-chart-color-square: #ff4444',              # Softer red
            '--kerykeion-chart-color-trine: #00ff00': '--kerykeion-chart-color-trine: #33ff33',                # Slightly softer green
            '--kerykeion-chart-color-opposition: #9932cc': '--kerykeion-chart-color-opposition: #b454e6',      # Brighter orchid

            # Planet and celestial body colors - optimized for dark background readability
            # Strategy: Convert all dark base colors to bright pastels while preserving color families

            # Major Planets
            '--kerykeion-chart-color-sun: #984b00': '--kerykeion-chart-color-sun: #ffd966',                   # Dark orange → bright golden yellow
            '--kerykeion-chart-color-moon: #150052': '--kerykeion-chart-color-moon: #e8e8ff',                 # Dark purple-blue → very light lavender-white
            '--kerykeion-chart-color-mercury: #520800': '--kerykeion-chart-color-mercury: #ffcc99',           # Dark red-brown → bright peach
            '--kerykeion-chart-color-venus: #400052': '--kerykeion-chart-color-venus: #ffccff',               # Dark purple → bright pink-lavender
            '--kerykeion-chart-color-mars: #540000': '--kerykeion-chart-color-mars: #ff9999',                 # Dark red → bright coral-red
            '--kerykeion-chart-color-jupiter: #47133d': '--kerykeion-chart-color-jupiter: #cc99ff',           # Dark purple → bright purple
            '--kerykeion-chart-color-saturn: #124500': '--kerykeion-chart-color-saturn: #ccddaa',             # Dark green → bright sage green
            '--kerykeion-chart-color-uranus: #6f0766': '--kerykeion-chart-color-uranus: #ff99ff',             # Dark magenta → bright magenta-pink
            '--kerykeion-chart-color-neptune: #06537f': '--kerykeion-chart-color-neptune: #99ccff',           # Dark blue → bright sky blue
            '--kerykeion-chart-color-pluto: #713f04': '--kerykeion-chart-color-pluto: #ffcc99',               # Dark brown → bright tan-orange

            # Lunar Nodes
            '--kerykeion-chart-color-mean-node: #4c1541': '--kerykeion-chart-color-mean-node: #ffaa66',       # Dark purple → bright orange
            '--kerykeion-chart-color-true-node: #4c1541': '--kerykeion-chart-color-true-node: #ffaa66',       # Dark purple → bright orange

            # Chiron & Lilith
            '--kerykeion-chart-color-chiron: #666f06': '--kerykeion-chart-color-chiron: #ffff99',             # Dark olive → bright yellow-green
            '--kerykeion-chart-color-mean-lilith: #000000': '--kerykeion-chart-color-mean-lilith: #ff66cc',   # Black → bright magenta-pink
            '--kerykeion-chart-color-true-lilith: #333333': '--kerykeion-chart-color-true-lilith: #ff66cc',   # Dark gray → bright magenta-pink

            # House Cusps (Angles)
            '--kerykeion-chart-color-first-house: #ff7e00': '--kerykeion-chart-color-first-house: #ffaa44',   # Orange → bright orange (Ascendant)
            '--kerykeion-chart-color-fourth-house: #000000': '--kerykeion-chart-color-fourth-house: #cccccc', # Black → light gray (IC)
            '--kerykeion-chart-color-seventh-house: #0000ff': '--kerykeion-chart-color-seventh-house: #6699ff', # Blue → bright blue (Descendant)
            '--kerykeion-chart-color-tenth-house: #ff0000': '--kerykeion-chart-color-tenth-house: #ff6666',   # Red → bright red (MC)

            # Lunar Phase - make dark portion visible on dark background
            '--kerykeion-chart-color-lunar-phase-0: #000000': '--kerykeion-chart-color-lunar-phase-0: #888888', # Dark part: black → medium gray (clearly visible)
            '--kerykeion-chart-color-lunar-phase-1: #ffffff': '--kerykeion-chart-color-lunar-phase-1: #f5f5f5', # Light part: white → very bright

            # Element percentages - bright, readable colors for dark mode
            '--kerykeion-chart-color-fire-percentage: #ff6600': '--kerykeion-chart-color-fire-percentage: #ffaa66',     # Fire: orange → bright orange
            '--kerykeion-chart-color-earth-percentage: #6a2d04': '--kerykeion-chart-color-earth-percentage: #e6c49a',   # Earth: dark brown → bright tan
            '--kerykeion-chart-color-air-percentage: #6f76d1': '--kerykeion-chart-color-air-percentage: #a0a8ff',       # Air: purple-blue → bright periwinkle
            '--kerykeion-chart-color-water-percentage: #630e73': '--kerykeion-chart-color-water-percentage: #dd99ff',   # Water: dark purple → bright lavender
        }

        # Apply dark theme colors
        for old_color, new_color in color_map.items():
            svg_content = svg_content.replace(old_color, new_color)

        # Adjust background style attribute
        svg_content = re.sub(
            r"style='background-color: var\(--kerykeion-chart-color-paper-1\)'",
            r"style='background-color: var(--kerykeion-chart-color-paper-1)'",
            svg_content
        )

    # Light theme is already applied by default from Kerykeion
    return svg_content


def enhance_typography(svg_content):
    """Enhance typography with refined font hierarchy and spacing.

    Typography system (optimized for screen readability, 36% larger):
    - Title: 40px/700 (prominent, bold)
    - Section labels: 20px/600 (semibold, highly readable)
    - Data values: 20px/400 (large, clear)
    - Metadata: 20px/400 (consistent with data)
    """
    # Enhance title: larger and bolder
    svg_content = re.sub(
        r"font-size: 28px; font-weight: 600",
        r"font-size: 40px; font-weight: 700; letter-spacing: -0.3px",
        svg_content
    )

    # Make section labels semibold (Elements:, Qualities:, planet names, cusp labels)
    # Elements and Qualities headers
    svg_content = re.sub(
        r"(<text[^>]*>)(Elements:|Qualities:)",
        r"\1<tspan style='font-weight: 600'>\2</tspan>",
        svg_content
    )

    # Planet names in grid (Sun, Moon, etc.) - make semibold
    for planet in ['Sun:', 'Moon:', 'Mercury:', 'Venus:', 'Mars:', 'Jupiter:', 'Saturn:',
                   'Uranus:', 'Neptune:', 'Pluto:', 'N. Node:', 'S. Node:']:
        svg_content = re.sub(
            rf"(<text[^>]*>){planet}",
            rf"\1<tspan style='font-weight: 600'>{planet}</tspan>",
            svg_content
        )

    # House cusp labels - make semibold
    for i in range(1, 13):
        svg_content = re.sub(
            rf"(<text[^>]*>)(Cusp {i}:)",
            rf"\1<tspan style='font-weight: 600'>\2</tspan>",
            svg_content
        )

    # Increase base font size for screen readability (9px → 18px)
    svg_content = re.sub(
        r"font-size: 9px",
        r"font-size: 18px",
        svg_content
    )

    # Also increase 10px text to 18px for consistency
    svg_content = re.sub(
        r"font-size: 10px",
        r"font-size: 18px",
        svg_content
    )

    return svg_content


def adjust_grid_spacing(svg_content):
    """Adjust vertical spacing in grids to accommodate larger 18px font.

    Original spacing was designed for 9-10px text (~14px line height).
    New spacing for 18px text needs ~26px line height for readability.
    Scale factor: 26/14 ≈ 1.86
    """
    def scale_spacing(y_val_str):
        y_val = int(y_val_str)
        if y_val == 0:
            return y_val_str
        # Scale up: 10→19, 24→45, 38→71, 52→97, etc.
        new_y = round(y_val * 1.86)
        return str(new_y)

    # Extract and adjust Main_Planet_Grid section
    planet_grid_match = re.search(
        r"(<g kr:node='Main_Planet_Grid'[^>]*>)(.*?)(</g>\s*<!-- 7\. House Cusps)",
        svg_content,
        re.DOTALL
    )
    if planet_grid_match:
        prefix = planet_grid_match.group(1)
        grid_content = planet_grid_match.group(2)
        suffix = planet_grid_match.group(3)

        # Adjust all translate(0,Y) in this section
        grid_content = re.sub(
            r"translate\(0,(\d+)\)",
            lambda m: f"translate(0,{scale_spacing(m.group(1))})",
            grid_content
        )

        svg_content = svg_content.replace(planet_grid_match.group(0), prefix + grid_content + suffix)

    # House cusps grid
    svg_content = re.sub(
        r"(<g transform='translate\(0,)(\d+)(\)'><text[^>]*><tspan[^>]*>Cusp)",
        lambda m: m.group(1) + scale_spacing(m.group(2)) + m.group(3),
        svg_content
    )

    # Extract and adjust Elements_Percentages section (uses y='...' not translate)
    elements_match = re.search(
        r"(<g kr:node='Elements_Percentages'[^>]*>)(.*?)(</g>\s*<!-- 9\. Qualities)",
        svg_content,
        re.DOTALL
    )
    if elements_match:
        prefix = elements_match.group(1)
        grid_content = elements_match.group(2)
        suffix = elements_match.group(3)

        # Adjust y='...' attributes (not translate)
        grid_content = re.sub(
            r"\sy='(\d+)'",
            lambda m: f" y='{scale_spacing(m.group(1))}'",
            grid_content
        )

        svg_content = svg_content.replace(elements_match.group(0), prefix + grid_content + suffix)

    # Extract and adjust Qualities_Percentages section (uses y='...' not translate)
    qualities_match = re.search(
        r"(<g kr:node='Qualities_Percentages'[^>]*>)(.*?)(</g>\s*<!-- 10\. Aspect List)",
        svg_content,
        re.DOTALL
    )
    if qualities_match:
        prefix = qualities_match.group(1)
        grid_content = qualities_match.group(2)
        suffix = qualities_match.group(3)

        # Adjust y='...' attributes (not translate)
        grid_content = re.sub(
            r"\sy='(\d+)'",
            lambda m: f" y='{scale_spacing(m.group(1))}'",
            grid_content
        )

        svg_content = svg_content.replace(qualities_match.group(0), prefix + grid_content + suffix)

    return svg_content


def scale_grid_symbols(svg_content):
    """Scale zodiac symbols and adjust positions to match larger 18px text.

    Font increased by 80% (10px → 18px), so symbols should scale similarly.
    Planet symbols: 0.4 → 0.77
    Zodiac symbols: 0.3 → 0.55
    """
    # Scale planet symbols in planetary grid (0.4 → 0.77)
    svg_content = re.sub(
        r"<use transform='scale\(0\.4\)' xlink:href='#(Sun|Moon|Mercury|Venus|Mars|Jupiter|Saturn|Uranus|Neptune|Pluto|True_North_Lunar_Node|Chiron|Ascendant|Medium_Coeli|Descendant|Imum_Coeli|Mean_Lilith|True_South_Lunar_Node)' />",
        r"<use transform='scale(0.77)' xlink:href='#\1' />",
        svg_content
    )

    # Adjust planet symbol position in planetary grid
    # translate(5,-8) × (0.77/0.4) ≈ translate(10,-15)
    svg_content = re.sub(
        r"<g transform='translate\(5,-8\)'><use transform='scale\(0\.77\)'",
        r"<g transform='translate(10,-15)'><use transform='scale(0.77)'",
        svg_content
    )

    # Adjust degree text position in planetary grid
    svg_content = re.sub(
        r"(scale\(0\.77\)' xlink:href='#[^']+' /></g><text text-anchor='start' )x='19'",
        r"\1x='42'",
        svg_content
    )

    # Scale zodiac symbols in planetary grid (0.3 → 0.50)
    svg_content = re.sub(
        r"<use transform='scale\(0\.3\)' xlink:href='#(Ari|Tau|Gem|Can|Leo|Vir|Lib|Sco|Sag|Cap|Aqu|Pis)' />",
        r"<use transform='scale(0.50)' xlink:href='#\1' />",
        svg_content
    )

    # Adjust zodiac symbol horizontal position to accommodate wider text
    svg_content = re.sub(
        r"<g transform='translate\(75,-8\)'><use transform='scale\(0\.50\)'",
        r"<g transform='translate(126,-15)'><use transform='scale(0.50)'",
        svg_content
    )

    # Adjust retrograde symbol scale and position (0.5 → 0.85)
    svg_content = re.sub(
        r"<use transform='scale\(\.5\)' xlink:href='#retrograde'",
        r"<use transform='scale(0.85)' xlink:href='#retrograde'",
        svg_content
    )

    # Adjust retrograde position
    svg_content = re.sub(
        r"<g transform='translate\(89,-6\)'><use transform='scale\(0\.85\)'",
        r"<g transform='translate(141,-13)'><use transform='scale(0.85)'",
        svg_content
    )

    # House cusp symbols: scale to 0.50 (matching planetary grid zodiac) and adjust position
    # Find in house cusps grid specifically
    def fix_house_cusp_symbols(content):
        # First update scale from 0.3 to 0.50
        content = re.sub(
            r"(<g transform='translate\([^)]+\)'>)<use transform='scale\(0\.3\)' xlink:href='#(Ari|Tau|Gem|Can|Leo|Vir|Lib|Sco|Sag|Cap|Aqu|Pis)' />",
            r"\1<use transform='scale(0.50)' xlink:href='#\2' />",
            content
        )
        # Pattern: match any existing translate pattern in house cusps grid (near "Cusp X:")
        # Adjust for 18px text and move to x=75
        content = re.sub(
            r"(Cusp \d+:</tspan></text>)<g transform='translate\([^)]+\)'>",
            r"\1<g transform='translate(75,-15)'>",
            content
        )
        return content

    svg_content = fix_house_cusp_symbols(svg_content)

    # Adjust house cusp degree text position within house grid
    # Adjust for 18px text - move degrees to x=103 and remove leading space
    # Only target text after cusp labels
    def adjust_cusp_degree_position(match):
        # Replace any x='number' with x='103' and remove leading space
        import re
        result = re.sub(r"x='\d+'", "x='103'", match.group(0))
        result = re.sub(r"(>)\s+(\d+°)", r"\1\2", result)  # Remove space after >
        return result

    svg_content = re.sub(
        r"(Cusp \d+:.*?)<text x='\d+'[^>]*>\s*\d+°\d+'\d+'</text>",
        adjust_cusp_degree_position,
        svg_content
    )

    return svg_content


def enhance_wheel_aesthetics(svg_content, theme='light'):
    """Enhance the zodiac wheel with refined visual styling.

    Args:
        theme: 'light' or 'dark' - adjusts shadow/glow for background

    Improvements:
    - Add subtle drop shadow (light) or glow (dark) to wheel
    - Increase planet symbol size
    - Refine aspect line weights
    """
    # Choose filter based on theme
    if theme == 'dark':
        # Dark mode: subtle glow instead of shadow
        filter_def = """
    <!-- Enhanced wheel styling (dark mode) -->
    <defs>
        <filter id="wheel-effect" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.4"/>
            </feComponentTransfer>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>"""
    else:
        # Light mode: traditional drop shadow
        filter_def = """
    <!-- Enhanced wheel styling (light mode) -->
    <defs>
        <filter id="wheel-effect" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
            <feOffset dx="0" dy="2" result="offsetblur"/>
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.3"/>
            </feComponentTransfer>
            <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>"""

    # Insert filter after the first defs section
    svg_content = re.sub(
        r"(</defs>)",
        r"\1\n    " + filter_def,
        svg_content,
        count=1
    )

    # Apply effect filter to the wheel
    svg_content = re.sub(
        r"(<g kr:node='Full_Wheel'[^>]*>)",
        r"\1\n        <g style='filter: url(#wheel-effect)'>",
        svg_content
    )

    # Close the filter group at the end of Full_Wheel
    # Pattern now accounts for header section between wheel and planetary grid
    svg_content = re.sub(
        r"(</g>\s*<!-- Minimal header)",
        r"</g>\n    \1",
        svg_content
    )

    # Make planet symbols in the wheel slightly larger (0.4 -> 0.45 scale)
    # Only target symbols within the zodiac ring, not in grids
    # Pattern now accounts for header section between wheel and planetary grid
    wheel_section_match = re.search(
        r"(<g kr:node='Full_Wheel'.*?</g>\s*<!-- Minimal header)",
        svg_content,
        re.DOTALL
    )

    if wheel_section_match:
        wheel_section = wheel_section_match.group(1)
        # Increase planet symbol scale within wheel
        wheel_section = re.sub(
            r"transform='scale\(0\.4\)'",
            r"transform='scale(0.45)'",
            wheel_section
        )
        svg_content = svg_content.replace(wheel_section_match.group(1), wheel_section)

    # Make aspect lines slightly more prominent
    svg_content = re.sub(
        r"(--kerykeion-chart-color-conjunction: #[0-9a-fA-F]{6})",
        r"\1; stroke-width: 1.5",
        svg_content
    )

    return svg_content


def enhance_aspect_grid_aesthetics(svg_content, theme='light'):
    """Enhance the aspect grid with refined visual styling.

    Args:
        theme: 'light' or 'dark' - adjusts shadow/glow for background

    Improvements:
    - Add subtle drop shadow (light) or glow (dark) to grid
    - Refine cell borders
    - Enhance aspect symbols
    """
    # Choose filter based on theme
    if theme == 'dark':
        # Dark mode: subtle glow
        filter_def = """
    <!-- Enhanced aspect grid styling (dark mode) -->
    <filter id="aspect-grid-effect" x="-10%" y="-10%" width="120%" height="120%">
        <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
        <feComponentTransfer>
            <feFuncA type="linear" slope="0.3"/>
        </feComponentTransfer>
        <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>"""
    else:
        # Light mode: traditional drop shadow
        filter_def = """
    <!-- Enhanced aspect grid styling (light mode) -->
    <filter id="aspect-grid-effect" x="-10%" y="-10%" width="120%" height="120%">
        <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>
        <feOffset dx="0" dy="1" result="offsetblur"/>
        <feComponentTransfer>
            <feFuncA type="linear" slope="0.2"/>
        </feComponentTransfer>
        <feMerge>
            <feMergeNode/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>"""

    # Insert filter after existing defs
    svg_content = re.sub(
        r"(<!-- Enhanced wheel styling.*?</filter>)",
        r"\1\n    " + filter_def,
        svg_content,
        flags=re.DOTALL
    )

    # Apply effect filter to both aspect list and aspect grid
    svg_content = re.sub(
        r"(<g kr:node='Aspect_List'[^>]*>)",
        r"\1\n        <g style='filter: url(#aspect-grid-effect)'>",
        svg_content
    )

    svg_content = re.sub(
        r"(<g kr:node='Aspect_Grid'[^>]*>)",
        r"\1\n        <g style='filter: url(#aspect-grid-effect)'>",
        svg_content
    )

    # Close the filter groups
    svg_content = re.sub(
        r"(</g>\s*<!-- 11\. Aspect Grid)",
        r"</g>\1",
        svg_content
    )

    svg_content = re.sub(
        r"(</svg>)",
        r"</g>\1",
        svg_content
    )

    # Refine cell borders - make them slightly more subtle but still visible
    svg_content = re.sub(
        r"stroke-width: 1px; stroke-width: 0\.5px",
        r"stroke-width: 0.6px; stroke-opacity: 0.8",
        svg_content
    )

    return svg_content


def create_minimal_header(title_text, location_content, lunar_text, moon_graphic, theme='light'):
    """Create a minimal, centered header with essential birth info and moon phase.

    Format (light mode - for print):
        [Name] (centered, larger, bold)
        [Date] • [Time] • [Location] • [Moon Icon] [Phase] (all inline)

    Format (dark mode - for screen):
        [Date] • [Time] • [Location] • [Moon Icon] [Phase] (all inline, no name)

    Args:
        title_text: Person's name from chart title
        location_content: Location metadata extracted from landscape SVG
        lunar_text: Lunar phase text (e.g., "Waning Gibbous")
        moon_graphic: Moon phase SVG graphic
        theme: 'light' (print, include name) or 'dark' (screen, no name)

    Returns:
        Centered header SVG markup
    """
    # Extract name from title (e.g., "Birth Chart - Joe Lewis" → "Joe Lewis")
    name = title_text.replace("Birth Chart", "").replace("-", "").strip()
    if not name or name == "Natal Chart":
        name = "Natal Chart"  # Fallback if no name provided

    # Extract location (e.g., "Location: South Williamson, US")
    location_match = re.search(r"Location:\s*([^<]+)", location_content)
    location = location_match.group(1).strip() if location_match else "Unknown"

    # Extract date/time (e.g., "1978-09-18 17:34 [-04:00]")
    datetime_match = re.search(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})", location_content)
    if datetime_match:
        date_raw = datetime_match.group(1)  # "1978-09-18"
        time_raw = datetime_match.group(2)  # "17:34"

        # Convert date to readable format: "1978-09-18" → "September 18, 1978"
        from datetime import datetime
        date_obj = datetime.strptime(date_raw, "%Y-%m-%d")
        date_formatted = date_obj.strftime("%B %d, %Y")

        # Convert time to 12-hour format: "17:34" → "5:34 PM"
        time_obj = datetime.strptime(time_raw, "%H:%M")
        time_formatted = time_obj.strftime("%-I:%M %p")  # %-I removes leading zero
    else:
        date_formatted = "Date Unknown"
        time_formatted = ""

    # Clean up lunar phase text: "Lunar phase: Waning Gibbous" → "Waning Gibbous"
    lunar_phase = lunar_text.replace("Lunar phase: ", "").strip()

    # Create centered inline layout with moon icon
    # Strategy: Build as left-aligned elements, then center the container group
    if theme == 'dark':
        # Dark mode: Three centered lines - birth info, moon icon (scaled 1.4x), moon phase text
        # Moon graphic has internal cx=20, cy=10. After 1.4x scale, adjusted translation keeps it centered
        header_svg = f"""<g kr:node='Minimal_Header'>
    <text x='400' y='0' text-anchor='middle' style='fill: var(--kerykeion-chart-color-paper-0); font-size: 18px;'>{date_formatted} • {time_formatted} • {location}</text>
    <g transform='translate(372,9) scale(1.4)'>
        {moon_graphic}
    </g>
    <text x='400' y='60' text-anchor='middle' style='fill: var(--kerykeion-chart-color-paper-0); font-size: 18px;'>{lunar_phase}</text>
</g>"""
    else:
        # Light mode: Name on first line, birth info on second line (location and lunar removed for debugging)
        birth_info_text = f"{date_formatted} • {time_formatted}"
        header_svg = f"""<g kr:node='Minimal_Header'>
    <text x='400' y='0' style='fill: var(--kerykeion-chart-color-paper-0); font-size: 24px !important; font-weight: 600; letter-spacing: -0.3px; text-anchor: middle !important;'>{name}</text>
    <text x='400' y='22' style='fill: var(--kerykeion-chart-color-paper-0); font-size: 12px !important; font-weight: 400; text-anchor: middle !important;'>{birth_info_text}</text>
</g>"""

    return header_svg


def build_portrait_chart(landscape_svg, theme='light'):
    """Build portrait chart with enhanced typography and wheel aesthetics.

    Args:
        theme: 'light' (white bg, for print) or 'dark' (dark bg, for screen)

    Elements included:
    1. Minimal header - centered (name, date/time/location, moon phase)
    2. Wheel - centered with shadow/glow and refined styling
    3. Planetary grid, house cusps, elements, qualities, aspects
    """

    # Extract style (CSS colors, fonts)
    style = extract_section(landscape_svg, r'(<style[^>]*>.*?</style>)')

    # Add SF Pro font family if not already present
    if 'SF Pro' not in style:
        style = style.replace('<style', '<style', 1).replace('>', '>\n        text { font-family: \'SF Pro\', \'SF Pro Display\', \'-apple-system\', \'Helvetica Neue\', sans-serif; }\n        ', 1)

    # Extract ALL defs sections (there may be multiple - one with clipPaths, one with symbols)
    defs_matches = re.findall(r'(<defs[^>]*>.*?</defs>)', landscape_svg, re.DOTALL)
    defs = '\n    '.join(defs_matches) if defs_matches else ''

    # 1. Extract title text
    title_match = re.search(r"kr:node='Chart_Title'[^>]*>([^<]+)<", landscape_svg)
    title_text = title_match.group(1) if title_match else 'Birth Chart'

    # Helper function to extract group content with proper nesting
    def extract_group_content(svg, node_name):
        """Extract content between opening and closing g tags, handling nested groups."""
        # Find the opening tag
        pattern = rf"<g kr:node='{node_name}'[^>]*>"
        match = re.search(pattern, svg)
        if not match:
            return ''

        start = match.end()
        depth = 1
        pos = start

        # Track nested <g> and </g> tags
        while pos < len(svg) and depth > 0:
            next_open = svg.find('<g ', pos)
            next_close = svg.find('</g>', pos)

            if next_close == -1:
                break

            if next_open != -1 and next_open < next_close:
                depth += 1
                pos = next_open + 1
            else:
                depth -= 1
                if depth == 0:
                    return svg[start:next_close]
                pos = next_close + 4

        return ''

    # 2. Extract zodiacal information and fix y-coordinates
    zodiac_content = extract_group_content(landscape_svg, 'Bottom_Left_Text')
    # Remove any Chart_Title elements (not part of zodiacal metadata)
    zodiac_content = re.sub(r"<text[^>]*kr:node='Chart_Title'[^>]*>.*?</text>", '', zodiac_content, flags=re.DOTALL)

    # Extract lunation/lunar text separately for moon phase section
    lunation_match = re.search(r"<text kr:node='Bottom_Left_Text_2'[^>]*>(Lunation Day:[^<]+)</text>", zodiac_content)
    lunar_match = re.search(r"<text kr:node='Bottom_Left_Text_3'[^>]*>(Lunar phase:[^<]+)</text>", zodiac_content)
    lunation_text = lunation_match.group(1) if lunation_match else 'Lunation Day: —'
    lunar_text = lunar_match.group(1) if lunar_match else 'Lunar phase: —'

    # Remove lunation/lunar text from zodiac_content (they'll go in moon phase section)
    zodiac_content = re.sub(r"<text kr:node='Bottom_Left_Text_[23]'[^>]*>.*?</text>", '', zodiac_content)

    # Only keep Bottom_Left_Text_0, 1, 4 (zodiacal info without lunation)
    # Adjust y-coordinates from landscape (452, 466, 508) to portrait (0, 15, 30)
    zodiac_content = re.sub(r"y='452'", "y='0'", zodiac_content)
    zodiac_content = re.sub(r"y='466'", "y='15'", zodiac_content)
    zodiac_content = re.sub(r"y='508'", "y='30'", zodiac_content)
    # Adjust x-coordinates to 0 (positioning handled by group transform at translate(10,40))
    zodiac_content = re.sub(r" x='20'", " x='0'", zodiac_content)

    # 3. Extract location metadata and fix y-coordinates
    location_content = extract_group_content(landscape_svg, 'Top_Left_Text')
    # Remove any Chart_Title elements (not part of location metadata)
    location_content = re.sub(r"<text[^>]*kr:node='Chart_Title'[^>]*>.*?</text>", '', location_content, flags=re.DOTALL)

    # Note: Location is already combined in landscape.svg by _combine_location_line()

    # Adjust y-coordinates from landscape to portrait
    # Location line is already combined in landscape by _combine_location_line()
    location_content = re.sub(r"y='58'", "y='0'", location_content)   # Location
    location_content = re.sub(r"y='70'", "y='15'", location_content)  # Latitude
    location_content = re.sub(r"y='82'", "y='30'", location_content)  # Longitude
    location_content = re.sub(r"y='94'", "y='45'", location_content)  # Date/Time
    location_content = re.sub(r"y='106'", "y='60'", location_content) # Day of Week
    # Adjust x-coordinates to 0 (positioning handled by group transform at translate(790,40))
    location_content = re.sub(r" x='20'", " x='0'", location_content)

    # Make location text right-aligned
    location_content = re.sub(
        r"(<text[^>]*kr:node='Top_Left_Text_[0-9]+'[^>]*)>",
        r"\1 text-anchor='end'>",
        location_content
    )

    # 4. Extract moon phase graphic for minimal header
    moon_graphic = extract_group_content(landscape_svg, 'Lunar_Phase')

    # Create minimal header (theme-aware: dark mode omits name, light mode includes it)
    minimal_header = create_minimal_header(title_text, location_content, lunar_text, moon_graphic, theme)

    # 5. Extract wheel
    wheel_content = extract_group_content(landscape_svg, 'Full_Wheel')

    # 6. Extract planetary positions grid using proper nested extraction
    planet_grid_raw = extract_group_content(landscape_svg, 'Main_Planet_Grid')
    # Remove the outer translate wrapper from landscape layout
    planet_grid_match = re.search(
        r"<g transform='translate\([^)]+\)'>(.*)</g>",
        planet_grid_raw,
        re.DOTALL
    )
    planet_grid_content = planet_grid_match.group(1) if planet_grid_match else planet_grid_raw

    # Move zodiac sign icons further right to avoid clipping degree text
    # Sign icons: translate(60,-8) → translate(75,-8)
    planet_grid_content = re.sub(
        r"<g transform='translate\(60,-8\)'>",
        r"<g transform='translate(75,-8)'>",
        planet_grid_content
    )

    # Move retrograde indicators proportionally
    # Retrograde: translate(74,-6) → translate(89,-6) (maintains 14px offset)
    planet_grid_content = re.sub(
        r"<g transform='translate\(74,-6\)'>",
        r"<g transform='translate(89,-6)'>",
        planet_grid_content
    )

    # 7. Extract house cusps grid
    houses_grid_raw = extract_group_content(landscape_svg, 'Main_Houses_Grid')
    # Remove the outer translate wrapper from landscape layout
    houses_grid_match = re.search(
        r"<g transform='translate\([^)]+\)'>(.*)</g>",
        houses_grid_raw,
        re.DOTALL
    )
    houses_grid_content = houses_grid_match.group(1) if houses_grid_match else houses_grid_raw

    # Remove non-breaking spaces from cusp labels
    houses_grid_content = re.sub(r"Cusp\s*(?:&#160;)*(\d+):", r"Cusp \1:", houses_grid_content)

    # Change cusp labels to left-aligned
    houses_grid_content = re.sub(r"text-anchor='end'", r"text-anchor='start'", houses_grid_content)
    # Change x from 40 to 0 for left alignment
    houses_grid_content = re.sub(r"(<text text-anchor='start' )x='40'", r"\1x='0'", houses_grid_content)

    # Add padding around zodiac sign symbols in cusps
    # Move sign symbols: translate(40,-8) → translate(64,-12) (24px padding, adjusted vertical alignment)
    houses_grid_content = re.sub(
        r"<g transform='translate\(40,-8\)'>",
        r"<g transform='translate(64,-12)'>",
        houses_grid_content
    )
    # Move degree text: x='53' → x='86' (adds padding after symbol)
    houses_grid_content = re.sub(r"x='53'", r"x='86'", houses_grid_content)

    # 8. Extract elements and qualities
    elements_content = extract_group_content(landscape_svg, 'Elements_Percentages')
    # Left-justify elements text (no text-anchor modification needed)
    # Remove x offset (positioning handled by group transform)
    elements_content = re.sub(r" x='20'", " x='0'", elements_content)
    qualities_content = extract_group_content(landscape_svg, 'Qualities_Percentages')
    # Left-justify qualities text (no text-anchor modification needed)
    # Remove x offset (positioning handled by group transform)
    qualities_content = re.sub(r" x='20'", " x='0'", qualities_content)

    # 9. Extract aspect grid
    aspect_grid_raw = extract_group_content(landscape_svg, 'Aspect_Grid')
    # Remove the outer translate wrapper from landscape layout
    aspect_grid_match = re.search(
        r"<g transform='translate\([^)]+\)'>(.*)</g>",
        aspect_grid_raw,
        re.DOTALL
    )
    aspect_grid_content = aspect_grid_match.group(1) if aspect_grid_match else aspect_grid_raw

    # Adjust aspect grid coordinates from absolute to relative
    # Subtract base offsets (x: 510, y: 230) to make coordinates relative to container
    def adjust_aspect_coords(content):
        # Store adjusted scaled coordinates with placeholders to prevent double-adjustment
        scaled_tags = []

        def store_scaled_coord(match):
            scale = float(match.group(1))
            x_val = float(match.group(2))
            y_val = float(match.group(3))
            href = match.group(4)

            # The x/y coordinates are in scaled coordinate space
            # Convert to actual position: x_actual = x_val * scale
            # Then subtract base offset and convert back to scaled space
            # Formula: new_x = (x_val * scale - offset) / scale
            actual_x = x_val * scale  # Convert to actual pixels
            actual_y = y_val * scale

            adjusted_x = actual_x - 510  # Subtract landscape base offset
            adjusted_y = actual_y - 230

            new_x = adjusted_x / scale  # Convert back to scaled coordinate space
            new_y = adjusted_y / scale

            # Store the adjusted tag
            adjusted_tag = f"<use transform='scale({scale})' x='{new_x}' y='{new_y}' xlink:href='{href}' />"
            placeholder = f"__SCALED_PLACEHOLDER_{len(scaled_tags)}__"
            scaled_tags.append(adjusted_tag)
            return placeholder

        # Replace scaled use tags with placeholders
        content = re.sub(
            r"<use transform='scale\(([\d.]+)\)'\s+x='([\d.]+)'\s+y='([\d.]+)'\s+xlink:href='([^']+)'\s*/>",
            store_scaled_coord,
            content
        )

        # Now adjust regular x/y attributes (won't touch placeholders)
        def fix_coord(match):
            attr = match.group(1)
            value = float(match.group(2))
            if attr == 'x' and value >= 510:
                new_value = value - 510
                return f"x='{new_value:.1f}'" if '.' in match.group(2) else f"x='{int(new_value)}'"
            elif attr == 'y' and value >= 230:
                new_value = value - 230
                return f"y='{new_value:.1f}'" if '.' in match.group(2) else f"y='{int(new_value)}'"
            return match.group(0)

        content = re.sub(r"(x|y)='([\d.]+)'", fix_coord, content)

        # Restore scaled tags from placeholders
        for i, adjusted_tag in enumerate(scaled_tags):
            content = content.replace(f"__SCALED_PLACEHOLDER_{i}__", adjusted_tag)

        return content

    aspect_grid_content = adjust_aspect_coords(aspect_grid_content)

    # Extract aspect list (planet headers for the aspect grid)
    aspect_list_raw = extract_group_content(landscape_svg, 'Aspect_List')
    # Remove the outer translate wrapper
    aspect_list_match = re.search(
        r"<g transform='translate\([^)]+\)'>(.*)</g>",
        aspect_list_raw,
        re.DOTALL
    )
    aspect_list_content = aspect_list_match.group(1) if aspect_list_match else aspect_list_raw
    # Adjust coordinates for aspect list
    aspect_list_content = adjust_aspect_coords(aspect_list_content)

    # Build portrait SVG
    portrait = f"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:kr='https://www.kerykeion.net/'
     width='800' height='1790' viewBox='0 0 800 1790'>
    <title>Natal Chart - Portrait</title>

    {style}

    {defs}

    <!-- Wheel (at top, scaled 1.417x with 60px margins on each side) -->
    <g kr:node='Full_Wheel' transform='translate(60,60) scale(1.417)'>
{wheel_content}
    </g>

    <!-- Minimal header (below wheel, centered) -->
    <g transform='translate(0,815)'>
        {minimal_header}
    </g>

    <!-- 6. Planetary Positions Grid (at 108,847) -->
    <g kr:node='Main_Planet_Grid' transform='translate(108,847)'>
{planet_grid_content}    </g>

    <!-- 7. House Cusps Grid (at 285,902) -->
    <g kr:node='Main_Houses_Grid' transform='translate(285,902)'>
{houses_grid_content}    </g>

    <!-- 8. Elements (at 490,664) -->
    <g kr:node='Elements_Percentages' transform='translate(490,664)'>
{elements_content}    </g>

    <!-- 9. Qualities (at 595,534) -->
    <g kr:node='Qualities_Percentages' transform='translate(595,534)'>
{qualities_content}    </g>

    <!-- 10. Aspect List (planet headers for aspect grid, full width from 20px edges) -->
    <g kr:node='Aspect_List' transform='translate(20,980) scale(3.0)'>
{aspect_list_content}    </g>

    <!-- 11. Aspect Grid (full width from 20px edges, scaled to fit 760px) -->
    <g kr:node='Aspect_Grid' transform='translate(20,980) scale(3.0)'>
{aspect_grid_content}    </g>

</svg>"""

    # Apply visual enhancements
    portrait = enhance_typography(portrait)
    portrait = adjust_grid_spacing(portrait)      # Fix line spacing for larger fonts
    portrait = scale_grid_symbols(portrait)       # Scale symbols to match text size
    portrait = enhance_wheel_aesthetics(portrait, theme=theme)
    portrait = enhance_aspect_grid_aesthetics(portrait, theme=theme)
    portrait = apply_color_theme(portrait, theme=theme)

    return portrait


if __name__ == '__main__':
    # Read landscape SVG from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            landscape_svg = f.read()
    else:
        landscape_svg = sys.stdin.read()

    # Determine output base path
    if len(sys.argv) > 2:
        output_base = sys.argv[2]
        # Remove .svg extension if present to use as base
        if output_base.endswith('.svg'):
            output_base = output_base[:-4]
    else:
        output_base = None

    # Build both light and dark versions
    portrait_light = build_portrait_chart(landscape_svg, theme='light')
    portrait_dark = build_portrait_chart(landscape_svg, theme='dark')

    # Write to files or stdout
    if output_base:
        light_path = f"{output_base}-light.svg"
        dark_path = f"{output_base}-dark.svg"

        with open(light_path, 'w') as f:
            f.write(portrait_light)
        with open(dark_path, 'w') as f:
            f.write(portrait_dark)

        print(f"✓ Light mode chart saved to {light_path}")
        print(f"✓ Dark mode chart saved to {dark_path}")
    else:
        # If no output file specified, print light version to stdout
        print(portrait_light)
