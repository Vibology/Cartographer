"""
Cartographer - Unified Archetypal Mapping Engine
=================================================

Complete API for archetypal cartography combining:
- Western Astrology (Kerykeion/Swiss Ephemeris)
- Human Design (IHDS mechanics)
- Cross-system synthesis

Endpoints:
- /astrology/* - Natal charts, transits, calculations
- /humandesign/* - Bodygraphs, mechanics, analysis
- /synthesis/* - Combined archetypal portraits
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import importlib.metadata

from .routers import astrology, humandesign, synthesis, transits, composite
from .utils.version import get_version

__version__ = get_version()

# Fallback to metadata if toml fails
if __version__ == "0.0.0":
    try:
        __version__ = importlib.metadata.version("cartographer")
    except importlib.metadata.PackageNotFoundError:
        pass

app = FastAPI(
    title="Cartographer",
    description="Unified Archetypal Mapping Engine - Astrology + Human Design",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(astrology.router, prefix="/astrology", tags=["Astrology"])
app.include_router(humandesign.router, prefix="/humandesign", tags=["Human Design"])
app.include_router(transits.router, prefix="/transits", tags=["HD Transits"])
app.include_router(composite.router, prefix="/composite", tags=["HD Relationships"])
app.include_router(synthesis.router, prefix="/synthesis", tags=["Synthesis"])

@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Cartographer",
        "version": __version__,
        "description": "Unified Archetypal Mapping Engine",
        "systems": {
            "astrology": "Western natal charts, transits, aspects",
            "humandesign": "Bodygraph calculations, mechanics, gates",
            "transits": "HD daily transits, solar returns, planetary weather",
            "composite": "HD relationship charts, Penta group dynamics",
            "synthesis": "Combined astrology + HD portraits"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "operational",
        "version": __version__,
        "systems": {
            "astrology": "kerykeion",
            "humandesign": "ihds",
            "ephemeris": "swisseph"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
