"""
EKOS Global Error Handling & Problem Details (RFC 7807) Middleware
Maps domain exceptions to RFC 7807 Problem Details JSON format.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-ErrorHandlers")

class EKOSDomainException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class EntityNotFoundError(EKOSDomainException):
    def __init__(self, entity_id: str):
        super().__init__(f"Entity '{entity_id}' not found in Knowledge Graph.", code="ENTITY_NOT_FOUND", status_code=404)

class PolicyViolationError(EKOSDomainException):
    def __init__(self, reason: str):
        super().__init__(f"Governance policy violation: {reason}", code="POLICY_VIOLATION", status_code=403)

async def ekos_exception_handler(request: Request, exc: EKOSDomainException):
    logger.error(f"Domain Error [{exc.code}] on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": f"https://ekos.io/errors/{exc.code.lower()}",
            "title": exc.code,
            "status": exc.status_code,
            "detail": exc.message,
            "instance": str(request.url.path)
        }
    )
