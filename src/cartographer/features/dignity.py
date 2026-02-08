"""
Comprehensive dignity calculation module implementing the full IHDS algorithm.

This module handles:
- No polarity detection (lines without exaltation or detriment)
- Juxtaposition detection via two scenarios:
  - Scenario A: Explicit star glyph (juxtaposition_planets)
  - Scenario B: Double fixing (one planet exalts, harmonic planet detriments)
- Harmonic fixing (channel partner planets affect each other)
- Single polarity states (exalted or detriment)

Algorithm priority order:
1. Check no_polarity flag
2. Check juxtaposition (star glyph or double fixing)
3. Check single polarity states
4. Return neutral if no triggers
"""

import json
import importlib.resources
from typing import Optional, Dict, List, Tuple

# Cache for dignity data
_dignity_data_cache: Optional[Dict] = None

# Channel definitions: (gate1, gate2) tuples
# Source: hd_constants.py GATES_CHAKRA_DICT
CHANNELS = [
    (64, 47), (61, 24), (63, 4), (17, 62), (43, 23), (11, 56),
    (16, 48), (20, 57), (20, 34), (20, 10), (31, 7), (8, 1),
    (33, 13), (45, 21), (35, 36), (12, 22), (32, 54), (28, 38),
    (57, 34), (50, 27), (18, 58), (10, 34), (15, 5), (2, 14),
    (46, 29), (10, 57), (25, 51), (59, 6), (42, 53), (3, 60),
    (9, 52), (26, 44), (40, 37), (49, 19), (55, 39), (30, 41)
]


def load_dignity_data() -> Dict:
    """
    Load comprehensive dignity data from JSON file.

    Returns cached data if already loaded.

    Returns:
        Dictionary with structure: {gate: {line: {exaltation_planets, detriment_planets, ...}}}
    """
    global _dignity_data_cache
    if _dignity_data_cache is not None:
        return _dignity_data_cache

    try:
        data_path = importlib.resources.files("humandesign.data").joinpath("exaltations_detriments.json")
        with data_path.open("r", encoding="utf-8") as f:
            _dignity_data_cache = json.load(f)
            return _dignity_data_cache
    except Exception as e:
        print(f"Error loading dignity data: {e}")
        return {}


def get_harmonic_gate(gate: int) -> Optional[int]:
    """
    Look up harmonic partner gate for a channel.

    Args:
        gate: Gate number to find harmonic partner for

    Returns:
        Harmonic gate number if gate is part of a channel, None otherwise
    """
    for gate1, gate2 in CHANNELS:
        if gate == gate1:
            return gate2
        elif gate == gate2:
            return gate1
    return None


def normalize_planet_name(planet: str) -> str:
    """
    Normalize planet name for matching.

    Handles variations like "North_Node" → "North Node"

    Args:
        planet: Planet name to normalize

    Returns:
        Normalized planet name
    """
    return planet.replace('_', ' ')


def calculate_dignity(
    gate: Optional[int],
    line: Optional[int],
    active_planet: str,
    harmonic_gate: Optional[int] = None,
    harmonic_planet: Optional[str] = None,
    dignity_data: Optional[Dict] = None
) -> Dict[str, Optional[str]]:
    """
    Calculate dignity state using full IHDS algorithm.

    Priority order:
    1. Check no_polarity flag
    2. Check juxtaposition - Scenario A (star glyph)
    3. Check juxtaposition - Scenario B (double fixing)
    4. Check single polarity states (exalted/detriment)
    5. Return neutral

    Args:
        gate: Gate number
        line: Line number (1-6)
        active_planet: Planet activating this gate.line
        harmonic_gate: Harmonic partner gate (if in a channel)
        harmonic_planet: Planet activating the harmonic gate
        dignity_data: Pre-loaded dignity data (loads if not provided)

    Returns:
        Dictionary with:
        - state: "exalted" | "detriment" | "juxtaposed" | "neutral"
        - active_trigger: Which planet triggered (if applicable)
        - harmonic_trigger: If harmonic contributed (if applicable)
        - details: Human-readable explanation
    """
    # Handle missing or invalid gate/line
    if gate is None or line is None:
        return {
            "state": "neutral",
            "active_trigger": None,
            "harmonic_trigger": None,
            "details": "Invalid gate or line"
        }

    # Load dignity data if not provided
    if dignity_data is None:
        dignity_data = load_dignity_data()

    # Check if data exists for this gate.line
    gate_str = str(gate)
    line_str = str(line)

    if gate_str not in dignity_data or line_str not in dignity_data[gate_str]:
        return {
            "state": "neutral",
            "active_trigger": None,
            "harmonic_trigger": None,
            "details": "No dignity data for this gate.line"
        }

    line_data = dignity_data[gate_str][line_str]

    # Normalize planet names
    active_planet = normalize_planet_name(active_planet)
    if harmonic_planet:
        harmonic_planet = normalize_planet_name(harmonic_planet)

    # Step 1: Check no_polarity flag
    if line_data.get("no_polarity", False):
        return {
            "state": "neutral",
            "active_trigger": None,
            "harmonic_trigger": None,
            "details": "No polarity line"
        }

    # Get planet lists
    exaltation_planets: List[str] = line_data.get("exaltation_planets", [])
    detriment_planets: List[str] = line_data.get("detriment_planets", [])
    juxtaposition_planets: List[str] = line_data.get("juxtaposition_planets", [])

    # Step 2: Check Juxtaposition - Scenario A (Star Glyph)
    if active_planet in juxtaposition_planets:
        return {
            "state": "juxtaposed",
            "active_trigger": active_planet,
            "harmonic_trigger": None,
            "details": "Star glyph (explicit juxtaposition)"
        }

    if harmonic_planet and harmonic_planet in juxtaposition_planets:
        return {
            "state": "juxtaposed",
            "active_trigger": None,
            "harmonic_trigger": harmonic_planet,
            "details": "Star glyph via harmonic planet"
        }

    # Check planet polarities
    active_exalted = active_planet in exaltation_planets
    active_detriment = active_planet in detriment_planets
    harmonic_exalted = harmonic_planet and harmonic_planet in exaltation_planets
    harmonic_detriment = harmonic_planet and harmonic_planet in detriment_planets

    # Step 3: Check Juxtaposition - Scenario B (Double Fixing)
    # One planet triggers exaltation, other triggers detriment
    if (active_exalted and harmonic_detriment) or (active_detriment and harmonic_exalted):
        return {
            "state": "juxtaposed",
            "active_trigger": active_planet,
            "harmonic_trigger": harmonic_planet,
            "details": "Double fixing (opposite polarities)"
        }

    # Step 4: Check Single Polarity States
    has_exaltation = active_exalted or harmonic_exalted
    has_detriment = active_detriment or harmonic_detriment

    if has_exaltation and has_detriment:
        # Both same polarity from multiple planets (e.g., Sun & Venus both exalt)
        # This is NOT juxtaposition (must be opposite polarities)
        # Return the active planet's polarity as primary
        if active_exalted:
            return {
                "state": "exalted",
                "active_trigger": active_planet,
                "harmonic_trigger": harmonic_planet if harmonic_exalted else None,
                "details": "Multiple planets same polarity (exalted)"
            }
        else:
            return {
                "state": "detriment",
                "active_trigger": active_planet,
                "harmonic_trigger": harmonic_planet if harmonic_detriment else None,
                "details": "Multiple planets same polarity (detriment)"
            }
    elif has_exaltation:
        trigger = active_planet if active_exalted else harmonic_planet
        source = "active" if active_exalted else "harmonic"
        return {
            "state": "exalted",
            "active_trigger": trigger,
            "harmonic_trigger": None,
            "details": f"Exalted via {source} planet"
        }
    elif has_detriment:
        trigger = active_planet if active_detriment else harmonic_planet
        source = "active" if active_detriment else "harmonic"
        return {
            "state": "detriment",
            "active_trigger": trigger,
            "harmonic_trigger": None,
            "details": f"Detriment via {source} planet"
        }
    else:
        return {
            "state": "neutral",
            "active_trigger": None,
            "harmonic_trigger": None,
            "details": "No dignity triggers"
        }
