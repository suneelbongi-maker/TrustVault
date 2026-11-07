# TrustVault – API Documentation

## 1. Introduction

TrustVault is a secure document-sharing web application developed using Python Flask. It provides authentication, role-based access control, document uploading, document listing, document downloading, and audit logging.

The application currently uses server-rendered HTML pages and Flask routes rather than JSON-based REST API responses.

## 2. Authentication

Users must authenticate before accessing protected pages and document operations.

### Login

- **Endpoint:** `/login`
- **Method:** GET, POST
- **Authentication:** Not required
- **Rate Limit:** 5 requests per minute

**Purpose:**
Allows users to sign in using their registered email address and password.

**Security checks:**
- Validates email format.
- Requires a password.
- Checks the account's active status.
- Verifies the password hash using Werkzeug.
- Clears the existing session before login.
- Supports the remember-me option.
- Uses CSRF protection.

**Response:**
- Successful login: Redirects to the dashboard.
- Invalid credentials: Displays an error message.

### Logout

- **Endpoint:** `/logout`
- **Method:** POST
- **Authentication:** Required
- **Allowed Roles:** All authenticated users

**Purpose:**
Logs out the currently authenticated user.

**Security checks:**
- Requires an authenticated session.
- Uses POST instead of GET.
- Protected by Flask-WTF CSRF protection.

**Response:**
Redirects the user to the login page.

## 3. Dashboard

### User Dashboard

- **Endpoint:** `/`
- **Method:** GET
- **Authentication:** Required
- **Allowed Roles:** All authenticated users

**Purpose:**
Displays the main dashboard for the logged-in user.

**Security checks:**
- Requires authentication through Flask-Login.

**Response:**
Displays `dashboard.html` with the current user's information.

### Admin Dashboard

- **Endpoint:** `/admin`
- **Method:** GET
- **Authentication:** Required
- **Allowed Roles:** Admin only

**Purpose:**
Provides an admin-only dashboard route.

**Security checks:**
- Requires authentication.
- Uses the `role_required("admin")` decorator.

**Response:**
Returns an admin access confirmation message.

**Error responses:**
- 401: User is not authenticated.
- 403: User does not have the admin role.

## 4. Document Management

### List Documents

- **Endpoint:** `/documents`
- **Method:** GET
- **Authentication:** Required
- **Allowed Roles:** All authenticated users

**Purpose:**
Displays the documents accessible to the current user.

**Permission checks:**
- Admin users can view all documents.
- Owners can view their own documents.
- Other users can view documents shared with them through a permission record.

**Response:**
Displays `documents.html` with the accessible documents and available categories.

### Upload Document

- **Endpoint:** `/documents/upload`
- **Method:** POST
- **Authentication:** Required
- **Allowed Roles:** Admin and Owner

**Purpose:**
Allows authorized users to upload documents.

**Required form fields:**
- `title`: Document title.
- `file`: Document file.
- `category_id`: Optional document category ID.

**Validation and security checks:**
- Checks that the title is provided.
- Checks that a file is selected.
- Uses `secure_filename()` to sanitize the original filename.
- Allows PDF, DOCX, TXT, PNG, JPG, and JPEG extensions.
- Rejects empty files.
- Enforces a maximum upload size of 10 MB.
- Validates the selected category.
- Generates a UUID-based storage filename.
- Calculates the SHA-256 file hash.
- Records a successful upload in the audit log.
- Rolls back the database transaction and removes the stored file if upload processing fails.

**Response:**
Redirects to the document listing page with a success or error message.

### Download Document

- **Endpoint:** `/documents/download/<document_id>`
- **Method:** GET
- **Authentication:** Required
- **Allowed Roles:** Admin, document owner, or user with a document permission record

**Purpose:**
Allows authorized users to download a stored document.

**Permission checks:**
- Admin users can download documents.
- Document owners can download their own documents.
- Users with a permission record for the document can download it.
- Unauthorized users receive HTTP 403.

**Security checks:**
- Checks whether the document exists.
- Verifies the user's access permission.
- Uses safe storage-path validation to prevent path traversal.
- Checks whether the stored file exists.
- Records successful and denied download attempts in the audit log.

**Response:**
Sends the requested document as a file attachment.

## 5. Endpoint Summary

| Endpoint | Method | Authentication | Access |
|---|---|---|---|
| `/login` | GET, POST | No | Public |
| `/logout` | POST | Yes | All authenticated users |
| `/` | GET | Yes | All authenticated users |
| `/admin` | GET | Yes | Admin |
| `/documents` | GET | Yes | All authenticated users |
| `/documents/upload` | POST | Yes | Admin, Owner |
| `/documents/download/<document_id>` | GET | Yes | Admin, Owner, Shared user |

## 6. HTTP Status Codes

| Status Code | Meaning |
|---|---|
| 200 | Request successful |
| 302 | Redirect after login, logout, or document operation |
| 401 | Authentication required |
| 403 | Access denied |
| 404 | Requested document or safe storage path not found |
| 500 | Internal server error, including certain audit logging failures |

## 7. Security Features

TrustVault implements the following security features:

1. Password hashing using Werkzeug with scrypt.
2. Flask-Login authentication.
3. Role-based access control.
4. CSRF protection using Flask-WTF.
5. Login rate limiting using Flask-Limiter.
6. Secure filename handling.
7. File extension and size validation.
8. UUID-based file storage names.
9. Safe storage-path validation.
10. SHA-256 file integrity hashes.
11. Audit logging with SHA-256 event hashes.
12. HTTP-only and SameSite session-cookie settings.

## 8. Important Implementation Notes

- The current routes return HTML pages, redirects, or file attachments; they do not expose JSON REST API responses.
- The application uses environment variables for configuration.
- The default rate-limit storage is in-memory. Redis is recommended for production.
- Production deployment should use HTTPS and enable secure session cookies.
- File extension validation does not replace file-content inspection or malware scanning.
- The audit hash chain should be independently verified and protected against database-level tampering.

## 9. Conclusion

TrustVault provides authenticated document management with role-based access control, controlled file sharing, secure file handling, and audit logging. Its Flask routes enforce access checks before displaying, uploading, or downloading documents.