import unittest
from backend.shared.security.audit_logger import CryptographicAuditLogger, AuditEntry

class TestCryptographicAuditLogger(unittest.TestCase):
    def setUp(self):
        self.logger = CryptographicAuditLogger()

    def test_log_event_creation(self):
        entry = self.logger.log_event(
            document_id="DOC-BRD-001",
            action="APPROVED",
            actor_id="user:USR-1092",
            payload={"change_severity": "MAJOR"}
        )
        self.assertEqual(entry.entry_id, "aud_1")
        self.assertIsNotNone(entry.checksum_hash)
        self.assertEqual(len(entry.checksum_hash), 64) # SHA-256 length

    def test_chain_integrity_verification_pass(self):
        self.logger.log_event("DOC-BRD-001", "DRAFT_CREATED", "user:USR-1092", {"v": 1})
        self.logger.log_event("DOC-BRD-001", "SECTION_UPDATED", "agent:AGT-GEN", {"v": 2})
        self.logger.log_event("DOC-BRD-001", "APPROVED", "user:USR-1092", {"v": 3})

        self.assertTrue(self.logger.verify_chain_integrity())

    def test_chain_integrity_tampering_detected(self):
        e1 = self.logger.log_event("DOC-BRD-001", "DRAFT_CREATED", "user:USR-1092", {"v": 1})
        e2 = self.logger.log_event("DOC-BRD-001", "APPROVED", "user:USR-1092", {"v": 2})

        # Simulate malicious tampering in audit entry payload
        e1.payload_json["v"] = 999

        self.assertFalse(self.logger.verify_chain_integrity())

if __name__ == "__main__":
    unittest.main()
