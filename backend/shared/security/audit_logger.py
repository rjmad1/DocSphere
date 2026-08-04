"""
EKOS Cryptographic Audit Logger & Tamper-Proof Audit Trail
Appends cryptographic SHA-256 checksum hashes to all entity mutations, approval decisions, and security events.
"""

import hashlib
import json
import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-AuditLogger")

class AuditEntry(BaseModel):
    entry_id: str
    document_id: str
    action: str  # ENTITY_CREATED, DRAFT_UPDATED, APPROVED, SECURITY_VIOLATION
    actor_id: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    payload_json: Dict[str, Any]
    previous_hash: str = "0000000000000000000000000000000000000000000000000000000000000000"
    checksum_hash: Optional[str] = None

class CryptographicAuditLogger:
    def __init__(self):
        self._audit_chain: List[AuditEntry] = []
        self._last_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        logger.info("Initialized CryptographicAuditLogger with SHA-256 checksum verification.")

    def calculate_checksum(self, entry: AuditEntry) -> str:
        raw_payload = f"{entry.entry_id}|{entry.document_id}|{entry.action}|{entry.actor_id}|{entry.timestamp}|{json.dumps(entry.payload_json, sort_keys=True)}|{entry.previous_hash}"
        return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

    def log_event(self, document_id: str, action: str, actor_id: str, payload: Dict[str, Any]) -> AuditEntry:
        entry_id = f"aud_{len(self._audit_chain)+1}"
        entry = AuditEntry(
            entry_id=entry_id,
            document_id=document_id,
            action=action,
            actor_id=actor_id,
            payload_json=payload,
            previous_hash=self._last_hash
        )
        entry.checksum_hash = self.calculate_checksum(entry)
        self._last_hash = entry.checksum_hash
        self._audit_chain.append(entry)

        logger.info(f"Audit Event Logged: ID={entry_id} Action={action} Hash={entry.checksum_hash[:12]}...")
        return entry

    def verify_chain_integrity(self) -> bool:
        prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        for entry in self._audit_chain:
            if entry.previous_hash != prev_hash:
                logger.error(f"AUDIT INTEGRITY FAILURE: Entry {entry.entry_id} previous_hash mismatch!")
                return False
            
            recomputed = self.calculate_checksum(entry)
            if entry.checksum_hash != recomputed:
                logger.error(f"AUDIT INTEGRITY FAILURE: Entry {entry.entry_id} checksum tampered!")
                return False

            prev_hash = entry.checksum_hash

        logger.info("Audit Chain Integrity Verified: 100% Valid Hash Chain.")
        return True
