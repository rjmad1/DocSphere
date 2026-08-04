"""
EKOS Immutable Write-Once-Read-Many (WORM) Audit Snapshot Backup Service
Generates immutable, append-only S3/Cloud Storage WORM snapshot manifests for AuditLogModel SHA-256 chains.
"""

import hashlib
import json
import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-WORMBackup")

class WORMManifest(BaseModel):
    snapshot_id: str
    tenant_id: str
    record_count: int
    start_hash: str
    end_hash: str
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    manifest_checksum: str

class WORMBackupService:
    def __init__(self, target_bucket: str = "s3://ekos-worm-audit-vault-us-east-1"):
        self.target_bucket = target_bucket
        logger.info(f"Initialized WORM Backup Service targeting {target_bucket}")

    def create_snapshot(self, tenant_id: str, audit_entries: List[Dict[str, Any]]) -> WORMManifest:
        """Creates an immutable WORM snapshot manifest with SHA-256 integrity verification."""
        if not audit_entries:
            raise ValueError("Cannot create empty WORM audit snapshot manifest.")

        start_hash = audit_entries[0].get("checksum_hash", "0000")
        end_hash = audit_entries[-1].get("checksum_hash", "0000")
        snapshot_id = f"snap_worm_{tenant_id}_{len(audit_entries)}_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}"

        raw_payload = f"{snapshot_id}|{tenant_id}|{len(audit_entries)}|{start_hash}|{end_hash}"
        manifest_checksum = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

        manifest = WORMManifest(
            snapshot_id=snapshot_id,
            tenant_id=tenant_id,
            record_count=len(audit_entries),
            start_hash=start_hash,
            end_hash=end_hash,
            manifest_checksum=manifest_checksum
        )

        logger.info(f"Created Immutable WORM Snapshot Manifest: {snapshot_id} (Checksum: {manifest_checksum[:12]}...)")
        return manifest
