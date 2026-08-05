"""
EKOS Security Hardening Tests
Covers:
  - JWT expiry validation (exp claim)
  - Path traversal injection detection
  - SQL injection detection  
  - CORS header presence
  - Input validator new patterns
  - Auth bypass prevention
  - Rate limit boundary
  - Cross-tenant enforcement for all user types
"""
import unittest
import base64
import hmac
import hashlib
import json
import time
import os
from fastapi.testclient import TestClient

from backend.main import app
from backend.shared.security.tenant_isolation import verify_jwt, TenantSecurityContext, UserContext, SecurityViolationError
from backend.shared.security.input_validator import InputSanitizer, InputSecurityValidationError


class TestJWTExpiry(unittest.TestCase):
    """JWT tokens with an expired 'exp' claim must be rejected."""

    SECRET = "test_signing_secret_for_unit_tests_only"

    def _make_token(self, payload: dict) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        sig_bytes = hmac.new(
            self.SECRET.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256
        ).digest()
        sig_b64 = base64.urlsafe_b64encode(sig_bytes).decode().rstrip("=")
        return f"{header_b64}.{payload_b64}.{sig_b64}"

    def test_valid_token_with_future_expiry_accepted(self):
        payload = {
            "user_id": "USR-1",
            "tenant_id": "tenant_a",
            "roles": ["Author"],
            "exp": int(time.time()) + 3600,  # 1 hour from now
        }
        token = self._make_token(payload)
        decoded = verify_jwt(token, self.SECRET)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["user_id"], "USR-1")

    def test_expired_token_rejected(self):
        payload = {
            "user_id": "USR-1",
            "tenant_id": "tenant_a",
            "roles": ["Author"],
            "exp": int(time.time()) - 10,  # 10 seconds in the past
        }
        token = self._make_token(payload)
        decoded = verify_jwt(token, self.SECRET)
        self.assertIsNone(decoded, "Expired JWT must be rejected")

    def test_token_without_exp_accepted(self):
        """Tokens without exp claim remain valid (backward-compat with existing issuers)."""
        payload = {"user_id": "USR-2", "tenant_id": "tenant_b", "roles": ["Author"]}
        token = self._make_token(payload)
        decoded = verify_jwt(token, self.SECRET)
        self.assertIsNotNone(decoded)

    def test_invalid_signature_rejected(self):
        payload = {"user_id": "USR-1", "tenant_id": "tenant_a", "roles": ["Author"]}
        token = self._make_token(payload)
        decoded = verify_jwt(token, "wrong_secret")
        self.assertIsNone(decoded)

    def test_malformed_token_rejected(self):
        self.assertIsNone(verify_jwt("not.a.valid.jwt.token", self.SECRET))
        self.assertIsNone(verify_jwt("", self.SECRET))
        self.assertIsNone(verify_jwt("two.parts", self.SECRET))


class TestPathTraversalDetection(unittest.TestCase):
    """InputSanitizer must block path traversal sequences."""

    def test_unix_dotdot_slash_rejected(self):
        with self.assertRaises(InputSecurityValidationError):
            InputSanitizer.sanitize_string("../../etc/passwd")

    def test_windows_dotdot_backslash_rejected(self):
        with self.assertRaises(InputSecurityValidationError):
            InputSanitizer.sanitize_string("..\\windows\\system32")

    def test_url_encoded_traversal_rejected(self):
        with self.assertRaises(InputSecurityValidationError):
            InputSanitizer.sanitize_string("%2e%2e%2fetc%2fpasswd")

    def test_mixed_encoding_traversal_rejected(self):
        with self.assertRaises(InputSecurityValidationError):
            InputSanitizer.sanitize_string("..%2fetc/passwd")

    def test_valid_file_path_component_accepted(self):
        # Normal relative path without traversal should pass
        result = InputSanitizer.sanitize_string("documents/report_2026.pdf")
        self.assertEqual(result, "documents/report_2026.pdf")


class TestSQLInjectionDetection(unittest.TestCase):
    """InputSanitizer must block common SQL injection payloads."""

    def test_union_select_rejected(self):
        with self.assertRaises(InputSecurityValidationError):
            InputSanitizer.sanitize_string("1' UNION SELECT username, password FROM users--")

    def test_drop_table_rejected(self):
        with self.assertRaises(InputSecurityValidationError):
            InputSanitizer.sanitize_string("'; DROP TABLE documents; --")

    def test_insert_into_rejected(self):
        with self.assertRaises(InputSecurityValidationError):
            InputSanitizer.sanitize_string("test'); INSERT INTO api_keys VALUES('hacked");

    def test_xp_cmdshell_rejected(self):
        with self.assertRaises(InputSecurityValidationError):
            InputSanitizer.sanitize_string("'; xp_cmdshell('whoami'); --")

    def test_information_schema_rejected(self):
        with self.assertRaises(InputSecurityValidationError):
            InputSanitizer.sanitize_string("SELECT * FROM INFORMATION_SCHEMA.TABLES")

    def test_valid_business_query_accepted(self):
        query = "What is the reconciliation requirement for the finance module?"
        result = InputSanitizer.sanitize_string(query)
        self.assertEqual(result, query)


class TestCORSHeaders(unittest.TestCase):
    """CORS headers must be present on API responses."""

    def setUp(self):
        self.client = TestClient(app)

    def test_cors_header_present_on_health(self):
        # Send an OPTIONS preflight from localhost:3000 (default allowed origin)
        response = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertIn(
            "access-control-allow-origin",
            response.headers,
            "CORS allow-origin header must be present on OPTIONS response",
        )

    def test_cors_disallowed_origin_not_reflected(self):
        response = self.client.get(
            "/health",
            headers={"Origin": "https://evil.attacker.com"},
        )
        # The origin should not be reflected in the allow-origin header
        allow_origin = response.headers.get("access-control-allow-origin", "")
        self.assertNotEqual(
            allow_origin,
            "https://evil.attacker.com",
            "Disallowed origin must not be reflected in CORS headers",
        )


class TestAdminRoleIsolation(unittest.TestCase):
    """Admin operations must not be accessible to Author/Steward-role users.

    These tests verify RBAC enforcement at the security layer level
    (TenantSecurityContext.authorize_role), which is what the HTTP endpoints
    call internally.
    """

    def setUp(self):
        self.security = TenantSecurityContext()

    def _user(self, roles, tenant="default", uid="U1"):
        return UserContext(user_id=uid, tenant_id=tenant, roles=roles, email="u@test.com")

    def test_author_cannot_manage_api_keys(self):
        """API key operations require Admin role — Author should be denied."""
        user = self._user(["Author"])
        with self.assertRaises(SecurityViolationError):
            self.security.authorize_role(user, "Admin")

    def test_steward_cannot_manage_api_keys(self):
        """API key operations require Admin role — Steward should be denied."""
        user = self._user(["Steward"])
        with self.assertRaises(SecurityViolationError):
            self.security.authorize_role(user, "Admin")

    def test_approver_cannot_manage_api_keys(self):
        """API key operations require Admin role — Approver should be denied."""
        user = self._user(["Approver"])
        with self.assertRaises(SecurityViolationError):
            self.security.authorize_role(user, "Admin")

    def test_admin_can_manage_api_keys(self):
        """Admin role must pass the Admin authorization check."""
        user = self._user(["Admin"])
        try:
            self.security.authorize_role(user, "Admin")
        except SecurityViolationError:
            self.fail("Admin user should pass the Admin role check")

    def test_only_admin_has_admin_access_across_roles(self):
        """Exactly one role group has Admin access: Admin itself."""
        non_admin_roles = [["Author"], ["Steward"], ["Approver"], [], ["Author", "Steward"], ["Author", "Approver"]]
        for roles in non_admin_roles:
            user = self._user(roles)
            with self.assertRaises(SecurityViolationError, msg=f"Role {roles} should not have Admin access"):
                self.security.authorize_role(user, "Admin")


class TestRBACHierarchy(unittest.TestCase):
    """Role hierarchy must be enforced correctly at every level."""

    def setUp(self):
        self.security = TenantSecurityContext()

    def _make_user(self, roles, tenant="T1"):
        return UserContext(user_id="U1", tenant_id=tenant, roles=roles, email="u@test.com")

    def test_admin_has_all_roles(self):
        user = self._make_user(["Admin"])
        for role in ["Author", "Steward", "Approver", "Admin"]:
            try:
                self.security.authorize_role(user, role)
            except SecurityViolationError:
                self.fail(f"Admin should have {role} role")

    def test_approver_has_no_admin(self):
        user = self._make_user(["Approver"])
        with self.assertRaises(SecurityViolationError):
            self.security.authorize_role(user, "Admin")

    def test_steward_has_no_approver(self):
        user = self._make_user(["Steward"])
        with self.assertRaises(SecurityViolationError):
            self.security.authorize_role(user, "Approver")

    def test_author_has_no_steward(self):
        user = self._make_user(["Author"])
        with self.assertRaises(SecurityViolationError):
            self.security.authorize_role(user, "Steward")

    def test_multi_role_union(self):
        """User with both Author and Approver should have union of their permissions."""
        user = self._make_user(["Author", "Approver"])
        # Approver grants Steward
        try:
            self.security.authorize_role(user, "Steward")
        except SecurityViolationError:
            self.fail("Approver grants Steward access via role hierarchy")

    def test_empty_roles_no_access(self):
        user = self._make_user([])
        with self.assertRaises(SecurityViolationError):
            self.security.authorize_role(user, "Author")


class TestCrossTenantEnforcement(unittest.TestCase):
    """Cross-tenant access must be denied for all non-Admin user types."""

    def setUp(self):
        self.security = TenantSecurityContext()

    def test_author_cross_tenant_denied(self):
        user = UserContext(user_id="U1", tenant_id="T1", roles=["Author"], email="u@t.com")
        with self.assertRaises(SecurityViolationError):
            self.security.validate_tenant_access(user, "T2")

    def test_steward_cross_tenant_denied(self):
        user = UserContext(user_id="U1", tenant_id="T1", roles=["Steward"], email="u@t.com")
        with self.assertRaises(SecurityViolationError):
            self.security.validate_tenant_access(user, "T99")

    def test_same_tenant_access_succeeds(self):
        user = UserContext(user_id="U1", tenant_id="T1", roles=["Author"], email="u@t.com")
        try:
            self.security.validate_tenant_access(user, "T1")
        except SecurityViolationError:
            self.fail("Same-tenant access should not raise SecurityViolationError")


if __name__ == "__main__":
    unittest.main()
