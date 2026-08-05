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

    def test_default_secrets_prevention(self):
        import os
        from backend.services.knowledge_engine.federated_graph_mesh import FederatedGraphMeshService
        from backend.shared.security.encryption import EnvelopeEncryptionService
        
        # Remove testing indicator temporarily to simulate production environment
        orig_pytest = os.environ.pop("PYTEST_CURRENT_TEST", None)
        orig_bypass = os.environ.pop("EKOS_BYPASS_AUTH_IN_TESTS", None)
        orig_master = os.environ.pop("EKOS_MASTER_KEY", None)
        try:
            # Should raise ValueError because EKOS_MASTER_KEY is not set and default key is prohibited in production
            with self.assertRaises(ValueError):
                EnvelopeEncryptionService()
                
            # Should raise ValueError because EKOS_MESH_SECRET is not set and default secret is prohibited in production
            with self.assertRaises(ValueError):
                FederatedGraphMeshService()
        finally:
            # Restore testing indicator
            if orig_pytest:
                os.environ["PYTEST_CURRENT_TEST"] = orig_pytest
            if orig_bypass:
                os.environ["EKOS_BYPASS_AUTH_IN_TESTS"] = orig_bypass
            if orig_master:
                os.environ["EKOS_MASTER_KEY"] = orig_master

    def test_jwt_signature_verification(self):
        import hmac
        import hashlib
        import base64
        import json
        from backend.shared.security.tenant_isolation import verify_jwt
        
        secret = "super_secure_enterprise_key_2026"
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {"user_id": "USR-99", "tenant_id": "tenant_abc", "roles": ["Author"]}
        
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        
        sig_bytes = hmac.new(
            secret.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256
        ).digest()
        sig_b64 = base64.urlsafe_b64encode(sig_bytes).decode().rstrip("=")
        
        token = f"{header_b64}.{payload_b64}.{sig_b64}"
        
        # Valid signature
        decoded = verify_jwt(token, secret)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["user_id"], "USR-99")
        
        # Invalid signature (wrong secret)
        decoded_invalid = verify_jwt(token, "wrong_secret")
        self.assertIsNone(decoded_invalid)

    def test_api_key_persistence(self):
        from backend.shared.security.api_key_manager import ApiKeyManager, ApiKeyScope
        akm = ApiKeyManager()
        
        # Create key
        res = akm.create_key("tenant_test_123", scopes=[ApiKeyScope.CHAT])
        self.assertIsNotNone(res.key_id)
        
        # Validate key
        validated = akm.validate_key(res.raw_key)
        self.assertIsNotNone(validated)
        self.assertEqual(validated.tenant_id, "tenant_test_123")
        
        # List keys
        keys = akm.list_keys("tenant_test_123")
        self.assertTrue(any(k.key_id == res.key_id for k in keys))
        
        # Revoke key
        revoked = akm.revoke_key(res.key_id)
        self.assertTrue(revoked)
        
        # Validate key again (should fail)
        validated_after = akm.validate_key(res.raw_key)
        self.assertIsNone(validated_after)

    def test_sliding_window_rate_limiter(self):
        from backend.shared.security.api_key_manager import ApiKeyManager
        akm = ApiKeyManager()
        
        res = akm.create_key("tenant_test_rate", rate_limit=3)
        key_id = res.key_id
        
        # First 3 requests should succeed
        self.assertTrue(akm.check_rate_limit(key_id))
        self.assertTrue(akm.check_rate_limit(key_id))
        self.assertTrue(akm.check_rate_limit(key_id))
        
        # 4th request should fail
        self.assertFalse(akm.check_rate_limit(key_id))

if __name__ == "__main__":
    unittest.main()
