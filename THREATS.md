# TrustVault – Security Threat Analysis

## 1. Introduction

TrustVault is a secure document-sharing application developed using Python Flask. It provides authentication, role-based access control, document upload and download, permission management, and audit logging.

This document identifies potential security threats and explains the security mechanisms implemented to reduce these risks.

## 2. Security Threats and Mitigation

### 2.1 Unauthorized Access and IDOR

**Threat:**

An attacker may attempt to access documents belonging to another user by changing document IDs in URLs or accessing restricted application features.

This is known as Insecure Direct Object Reference (IDOR).

**Mitigation implemented:**

- Flask-Login protects authenticated routes.
- Role-based access control restricts sensitive operations.
- The `role_required()` decorator checks whether users have the required role.
- Document listing is filtered based on ownership and sharing permissions.
- Download operations verify whether the user is an administrator, document owner, or authorized user.
- Unauthorized download attempts receive HTTP 403 responses.

**Related files:**
- `security/decorators.py`
- `routes/documents.py`
- `models/permission.py`

### ### 2.2 Password Attacks

**Threat:**

Attackers may attempt brute-force attacks, dictionary attacks, or repeatedly submit incorrect passwords to gain unauthorized access.

**Mitigation implemented:**

- Passwords are hashed using Werkzeug's `generate_password_hash()` function.
- The scrypt password-hashing algorithm is used.
- Plain-text passwords are not stored in the database.
- Password verification uses `check_password_hash()`.
- Login attempts are limited to 5 requests per minute using Flask-Limiter.
- Inactive accounts are prevented from logging in.
- Invalid login attempts return a generic error message to avoid revealing whether an email address exists.

**Related files:**
- `models/user.py`
- `routes/auth.py`
- `extensions.py`
- `config.py`

**Production recommendation:**

Configure persistent Redis storage for rate limiting instead of in-memory storage when deploying the application.

### 2.3 CSRF and Session Attacks

**Threat:**

Cross-Site Request Forgery (CSRF) may cause an authenticated user to submit unwanted requests.

Session attacks may attempt to misuse authentication cookies.

**Mitigation implemented:**

- Flask-WTF CSRF protection is enabled.
- HTTPOnly cookies prevent ordinary JavaScript from reading session cookies.
- SameSite is configured as Lax.
- Remember-me cookies also use HTTPOnly and SameSite settings.
- Secure cookie settings can be enabled through environment configuration.

**Related files:**
- `config.py`
- `extensions.py`
- `tests/test_csrf.py`

Production recommendation: Enable Secure cookies and HTTPS.

### 2.4 Unsafe File Uploads

**Threat:**

Attackers may upload unsupported, empty, oversized, or potentially dangerous files.

**Mitigation implemented:**

- Only PDF, DOCX, TXT, PNG, JPG, and JPEG extensions are accepted.
- Uploaded filenames are sanitized using `secure_filename()`.
- Empty files are rejected.
- File uploads are limited to 10 MB.
- UUID-based storage filenames prevent filename collisions.
- Uploaded files are stored separately in the uploads directory.
- SHA-256 checksums are calculated for uploaded documents.

**Related files:**
- `routes/documents.py`
- `config.py`

Future improvement: Add file-signature validation, malware scanning, and stricter content validation. Extension validation alone cannot guarantee that an uploaded file is safe.

### 2.5 Unauthorized Document Downloads

**Threat:**

A user may attempt to download documents without having the required permissions.

**Mitigation implemented:**

- Authentication is required before downloading.
- Administrators can access documents.
- Document owners can download their documents.
- Shared users must have a permission record.
- Unauthorized download attempts are denied with HTTP 403.
- Both successful and denied download attempts are recorded in audit logs.

**Related files:**
- `routes/documents.py`
- `models/permission.py`
- `models/document.py`

### 2.6 Path Traversal Attacks

**Threat:**

An attacker may attempt to manipulate file paths to access files outside the intended uploads directory.

**Mitigation implemented:**

- Storage filenames are checked for directory separators.
- Path objects are resolved before file access.
- The resolved path must remain inside the configured uploads directory.
- Invalid paths are rejected with HTTP 404.

**Related file:**
- `routes/documents.py`

### 2.7 Audit Log Tampering

**Threat:**

An attacker may attempt to modify or manipulate audit records to hide unauthorized activities.

**Mitigation implemented:**

- Audit events record the actor, document, action, result, IP address, and timestamp.
- SHA-256 hashes are generated for audit events.
- Each event stores the previous event's hash.
- This creates a hash-linked audit trail.
- Audit records are committed to the database.

**Related files:**
- `routes/documents.py`
- `models/audit_log.py`

Limitation: Hash chaining can help detect modifications when the chain is independently verified. It does not provide complete protection against an attacker who can modify the database and rebuild the chain.

Future improvement: Store audit records in an independently protected or append-only external logging system.

## 3. Additional Security Measures

TrustVault also includes:

- Environment-based configuration using `.env`.
- SQLAlchemy database integration.
- Database constraints for document permissions.
- Error handling for database and file operations.
- Database rollback when upload operations fail.
- UUID-based document storage identifiers.
- Configurable request rate-limiting storage.

## 4. Security Testing

The project includes automated security and functionality tests:

| Test file | Testing purpose |
|---|---|
| `test_auth.py` | Authentication functionality |
| `test_csrf.py` | CSRF protection |
| `test_documents.py` | Document operations and access control |
| `test_rate_limit.py` | Rate-limiting functionality |

Previously recorded test result:

- 35 tests passed.
- 1 test skipped.
- 1 warning.

These results represent the test run completed during development, not a guarantee of complete security.

## 5. Future Security Enhancements

The following improvements are recommended:

1. Add malware scanning for uploaded files.
2. Implement stronger password policies and verify login rate limits.
3. Add multi-factor authentication.
4. Introduce independent audit-log storage.
5. Validate uploaded file content and MIME signatures.
6. Enable HTTPS and secure session cookies in production.
7. Add automated audit-chain integrity verification.
8. Consider encryption at rest for sensitive documents.

## 6. Conclusion

TrustVault implements multiple security mechanisms to protect user accounts and shared documents. Authentication, role-based access control, CSRF protection, file validation, safe path resolution, download authorization, and hash-linked audit logging help reduce common application security risks.

Further security improvements and production configuration are necessary to strengthen the application before public deployment.