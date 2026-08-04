import logging
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("EKOS-ApiKeyManager")

class ApiKeyScope(str, Enum):
    """Scopes defining what an API key can access."""
    CHAT = "CHAT"
    SEARCH = "SEARCH"
    AGENTS = "AGENTS"
    ADMIN = "ADMIN"
    WIDGET = "WIDGET"

class ApiKey(BaseModel):
    """Internal representation of an API key."""
    key_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key_hash: str
    key_prefix: str
    tenant_id: str
    agent_id: Optional[str] = None
    scopes: List[ApiKeyScope] = Field(default_factory=list)
    rate_limit_per_minute: int = 60
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    is_active: bool = True
    last_used_at: Optional[datetime] = None
    usage_count: int = 0

class ApiKeyCreateResult(BaseModel):
    """Result returned when creating a new API key."""
    key_id: str
    raw_key: str
    key_prefix: str
    scopes: List[ApiKeyScope]

class ApiKeyManager:
    """Service for managing API key lifecycles."""
    
    def __init__(self):
        """Initialize the API key manager."""
        self._keys: Dict[str, ApiKey] = {}
        logger.info("Initialized ApiKeyManager.")

    def _hash_key(self, raw_key: str) -> str:
        """Hash a raw key using SHA-256."""
        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    def create_key(self, tenant_id: str, agent_id: Optional[str] = None, 
                   scopes: Optional[List[ApiKeyScope]] = None, 
                   rate_limit: int = 60, expires_hours: Optional[int] = None) -> ApiKeyCreateResult:
        """Create a new API key."""
        raw_key = f"ds_{uuid.uuid4().hex}"
        key_hash = self._hash_key(raw_key)
        key_prefix = raw_key[:8]
        
        expires_at = None
        if expires_hours:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
            
        api_key = ApiKey(
            key_hash=key_hash,
            key_prefix=key_prefix,
            tenant_id=tenant_id,
            agent_id=agent_id,
            scopes=scopes or [ApiKeyScope.CHAT, ApiKeyScope.SEARCH],
            rate_limit_per_minute=rate_limit,
            expires_at=expires_at
        )
        
        self._keys[api_key.key_id] = api_key
        logger.info(f"Created API key {api_key.key_id} for tenant {tenant_id}")
        
        return ApiKeyCreateResult(
            key_id=api_key.key_id,
            raw_key=raw_key,
            key_prefix=key_prefix,
            scopes=api_key.scopes
        )

    def validate_key(self, raw_key: str) -> Optional[ApiKey]:
        """Validate an API key and update its usage metrics."""
        key_hash = self._hash_key(raw_key)
        
        # Look up by hash
        matched_key = None
        for key in self._keys.values():
            if key.key_hash == key_hash:
                matched_key = key
                break
                
        if not matched_key:
            return None
            
        if not matched_key.is_active:
            return None
            
        if matched_key.expires_at and matched_key.expires_at < datetime.now(timezone.utc):
            matched_key.is_active = False
            return None
            
        # Update usage metrics
        matched_key.last_used_at = datetime.now(timezone.utc)
        matched_key.usage_count += 1
        
        return matched_key

    def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key by marking it inactive."""
        if key_id in self._keys:
            self._keys[key_id].is_active = False
            logger.info(f"Revoked API key: {key_id}")
            return True
        return False

    def list_keys(self, tenant_id: str) -> List[ApiKey]:
        """List all API keys for a tenant."""
        return [k for k in self._keys.values() if k.tenant_id == tenant_id]

    def check_rate_limit(self, key_id: str) -> bool:
        """Check if an API key has exceeded its rate limit."""
        if key_id not in self._keys:
            return False
            
        # Placeholder implementation for rate limit check
        # Production: Use Redis sliding window algorithm
        key = self._keys[key_id]
        if key.usage_count > key.rate_limit_per_minute * 1000: # mocked condition
            return False
        return True
