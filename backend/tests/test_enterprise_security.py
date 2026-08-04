import unittest
from backend.shared.security.tenant_isolation import TenantSecurityContext, UserContext, SecurityViolationError
from backend.shared.security.encryption import EnvelopeEncryptionService

class TestEnterpriseSecurity(unittest.TestCase):
    def setUp(self):
        self.security = TenantSecurityContext()
        self.encryption = EnvelopeEncryptionService(master_key="test_master_key_32b_secret")
        self.user = UserContext(
            user_id="USR-1092",
            tenant_id="tenant_sap_001",
            roles=["Steward"],
            email="steward@enterprise.com"
        )

    def test_tenant_access_success(self):
        # Accessing own tenant should succeed without error
        try:
            self.security.validate_tenant_access(self.user, "tenant_sap_001")
        except SecurityViolationError:
            self.fail("validate_tenant_access raised SecurityViolationError unexpectedly.")

    def test_cross_tenant_access_denied(self):
        # Accessing another tenant must raise SecurityViolationError
        with self.assertRaises(SecurityViolationError):
            self.security.validate_tenant_access(self.user, "tenant_other_999")

    def test_rbac_authorization(self):
        # Steward has Steward and Author rights
        try:
            self.security.authorize_role(self.user, "Author")
        except SecurityViolationError:
            self.fail("authorize_role failed for inherited Author role.")

        # Steward does NOT have Approver rights
        with self.assertRaises(SecurityViolationError):
            self.security.authorize_role(self.user, "Approver")

    def test_envelope_encryption_decryption(self):
        secret_text = "CONFIDENTIAL_FINANCIAL_METRIC_2026"
        ciphertext = self.encryption.encrypt_field(secret_text)
        self.assertNotEqual(secret_text, ciphertext)

        decrypted = self.encryption.decrypt_field(ciphertext)
        self.assertEqual(secret_text, decrypted)

if __name__ == "__main__":
    unittest.main()
