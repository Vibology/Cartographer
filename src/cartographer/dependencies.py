"""
Dependencies for Cartographer API

Note: Authentication disabled for local development.
Enable token verification by uncommenting the code below and setting HD_API_TOKEN.
"""

from fastapi import Header, HTTPException
import os

# Optional token verification (disabled by default for local use)
HD_API_TOKEN = os.getenv("HD_API_TOKEN", None)

async def verify_token(x_api_token: str = Header(None)):
    """
    Optional API token verification.

    To enable: Set HD_API_TOKEN environment variable.
    """
    if HD_API_TOKEN and x_api_token != HD_API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API token"
        )
    return True
