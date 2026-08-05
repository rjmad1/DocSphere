"""
EKOS SQLAlchemy Relational Models
Defines Document, ASST, AuditLog, and UserSession tables.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import datetime
from backend.shared.models.database import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True) # e.g. DOC-BRD-001
    title = Column(String, nullable=False)
    template_type = Column(String, nullable=False) # BRD, FRS, ADR, etc.
    version = Column(String, default="1.0.0")
    status = Column(String, default="DRAFT") # DRAFT, IN_REVIEW, APPROVED, DEPRECATED
    tenant_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    created_by = Column(String, nullable=False)

    asst_tree = Column(JSON, nullable=True) # Full ASST JSON snapshot
    metadata_json = Column(JSON, nullable=True)

    audit_logs = relationship("AuditLogModel", back_populates="document")

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    action = Column(String, nullable=False) # ENTITY_EXTRACTED, SECTION_REGENERATED, APPROVED, DEPRECATED
    actor_id = Column(String, nullable=False) # agent:AGT-GEN or user:USR-1092
    timestamp = Column(DateTime, default=utc_now)
    delta_json = Column(JSON, nullable=True)
    evidence_citation = Column(JSON, nullable=True)
    checksum_hash = Column(String, nullable=True)

    document = relationship("DocumentModel", back_populates="audit_logs")

class EntityMetadataModel(Base):
    __tablename__ = "entity_metadata"

    entity_id = Column(String, primary_key=True, index=True) # REQ-00847
    entity_type = Column(String, nullable=False, index=True) # BusinessRequirement
    canonical_name = Column(String, nullable=False)
    version = Column(String, default="1.0.0")
    state = Column(String, default="DRAFT")
    properties_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)

class ApiKeyModel(Base):
    __tablename__ = "api_keys"

    key_id = Column(String, primary_key=True, index=True)
    key_hash = Column(String, nullable=False, unique=True, index=True)
    key_prefix = Column(String, nullable=False)
    tenant_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=True)
    scopes = Column(JSON, nullable=False)  # Store list of scopes as JSON
    rate_limit_per_minute = Column(Integer, default=60)
    created_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)

