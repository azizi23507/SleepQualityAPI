from fastapi import  Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from config import settings
import logging
logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)
EXEMPT_PATH = {"/health"}

def verify_api_key(request: Request, api_key: str = Security(api_key_header)):
    if request.url.path in EXEMPT_PATH:
        return None
    if api_key is None or api_key != settings.api_key:
        logger.warning("Rejected request with invalid or missing API key")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or missing API key")
    return api_key