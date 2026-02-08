# Cartographer

**Unified Archetypal Mapping Engine** — Western Astrology + Human Design

Complete API for archetypal cartography combining precision calculations from two major systems:
- **Western Astrology** (Kerykeion/Swiss Ephemeris)
- **Human Design** (IHDS mechanics with enhanced bodygraph rendering)

---

## Features

### Astrology Endpoints

- **POST /astrology/calculate** — Complete natal chart calculation
  - Planetary positions (longitude, latitude, speed, retrograde)
  - House cusps (Placidus, Whole Sign, Koch, etc.)
  - Aspects with orbs and applying/separating
  - Lunar phase and nodes
  - Element/modality distribution

- **GET /astrology/chart** — Natal chart visualization (PNG, SVG, PDF)
- **GET /astrology/transits** — Current planetary positions

### Human Design Endpoints

- **POST /humandesign/calculate** — Complete Human Design chart
  - Type, Strategy, Authority, Profile, Cross
  - Defined/undefined centers and channels
  - All 64 gates with personality/design activations
  - Variables (arrows: PRL/DRR)
  - Dream Rave and Global Cycles

- **GET /humandesign/bodygraph** — Enhanced bodygraph visualization (SVG)
  - Luminous gradients for defined centers
  - Exaltation/detriment dignity symbols
  - Professional typography (Cabin font family)
  - Personality/Design activation panels

### Synthesis Endpoints

- **POST /synthesis/complete** — Combined archetypal portrait (JSON)
  - Both systems' data in one unified response
  - Cross-system resonance notes

- **POST /synthesis/charts** — Both visualizations (Base64 encoded)

---

## Installation

### Prerequisites

- Python 3.10+
- Swiss Ephemeris files (included with pyswisseph)

### Setup

```bash
# Clone repository
git clone https://github.com/Vibology/Cartographer.git
cd Cartographer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

---

## Usage

### Start the API Server

```bash
uvicorn src.cartographer.api:app --reload
```

Server runs at: http://localhost:8000

**API Documentation:**
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example: Calculate Natal Astrology Chart

```bash
curl -X POST "http://localhost:8000/astrology/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Person",
    "year": 1990,
    "month": 1,
    "day": 15,
    "hour": 12,
    "minute": 30,
    "lat": 40.7128,
    "lng": -74.0060,
    "tz_str": "America/New_York",
    "house_system": "P"
  }'
```

### Example: Generate Bodygraph

```bash
curl "http://localhost:8000/humandesign/bodygraph?name=Example&year=1990&month=1&day=15&hour=12&minute=30&place=New%20York,%20USA" \
  --output bodygraph.svg
```

### Example: Complete Synthesis

```bash
curl -X POST "http://localhost:8000/synthesis/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Person",
    "year": 1990,
    "month": 1,
    "day": 15,
    "hour": 12,
    "minute": 30,
    "lat": 40.7128,
    "lng": -74.0060,
    "tz_str": "America/New_York",
    "place": "New York, USA",
    "house_system": "P"
  }'
```

---

## Architecture

```
Cartographer/
├── src/cartographer/
│   ├── api.py                    # Main FastAPI application
│   ├── routers/
│   │   ├── astrology.py          # Astrology endpoints
│   │   ├── humandesign.py        # Human Design endpoints
│   │   └── synthesis.py          # Cross-system synthesis
│   ├── services/
│   │   ├── astro_calculator.py   # Kerykeion wrapper
│   │   ├── astro_renderer.py     # Chart generation
│   │   ├── hd_calculator.py      # HD calculations
│   │   └── chart_renderer.py     # Enhanced bodygraph renderer
│   ├── schemas/
│   │   ├── astrology.py          # Pydantic models (astrology)
│   │   ├── humandesign.py        # Pydantic models (HD)
│   │   └── synthesis.py          # Combined models
│   ├── features/
│   │   └── dignity.py            # HD dignity calculations
│   └── data/
│       ├── layout_data.json      # Bodygraph SVG paths
│       ├── exaltations_detriments.json
│       └── fonts/                # Cabin font family
```

---

## Custom Enhancements

### Human Design Bodygraph Renderer

- **Luminous gradients** — Defined centers glow with archetypal radiance
- **Dignity symbols** — Exaltation/detriment triangles on activated gates
- **Professional typography** — Cabin font family integration
- **Jovian Archive verified** — Line-level exaltation/detriment corrections
- **Complete IHDS algorithm** — Juxtaposition & harmonic fixing for dignities

### Data Sources

- **Swiss Ephemeris** — High-precision planetary positions
- **Kerykeion** — Modern Python astrology library
- **IHDS verified data** — Human Design mechanics
- **Jovian Archive** — Line-level dignity corrections

---

## Technology Stack

- **FastAPI** — Modern Python web framework
- **Kerykeion** — Astrology calculations
- **pyswisseph** — Swiss Ephemeris bindings
- **matplotlib** — Chart rendering
- **Pydantic** — Data validation

---

## License

MIT License — see LICENSE file

---

## Credits

**Built by Vibology**

Integrates:
- [Kerykeion](https://github.com/g-battaglia/kerykeion) — Astrology library
- [humandesign_api](https://github.com/dturkuler/humandesign_api) — HD calculations (fork with enhancements)
- Swiss Ephemeris — Astronomical calculations

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/Vibology/Cartographer/issues
- Email: joe@vibology.org
