import swisseph as swe
import logging

logger = logging.getLogger(__name__)

def check_swisseph_health() -> str:
    """
    Checks if Swiss Ephemeris is functioning correctly by performing a simple calculation.
    Returns "ready" if successful, "error" otherwise.
    """
    try:
        # Perform a calculation for the Sun at Julian Day 0 (arbitrary)
        # This will fail if the library isn't loaded or ephemeris files are missing.
        swe.calc_ut(2451545.0, swe.SUN)
        return "ready"
    except Exception as e:
        logger.error(f"Swiss Ephemeris health check failed: {e}")
        return "error"
