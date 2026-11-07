# TrustVault – Database Setup Guide

## 1. Overview

TrustVault uses MySQL as its relational database management system.

The database stores user accounts, document information, document categories, access permissions, and security audit logs.

**Database Name:** `trustvault`

**Database Engine:** MySQL

**Character Set:** utf8mb4

**Collation:** utf8mb4_unicode_ci

## 2. Prerequisites

Before setting up the database, install:

- MySQL Server 8.0 or later.
- MySQL Workbench (optional).
- Python 3.10 or later.
- TrustVault project dependencies.

## 3. Database Structure

TrustVault contains six main tables.

### users
Stores registered user information.

- id – Primary key.
- name – User's full name.
- email – Unique email address.
- password_hash – Hashed password.
- role – User role (admin, owner, viewer).
- is_active – Account status.
- created_at – Account creation timestamp.

### categories
Stores document categories.

- id – Primary key.
- name – Unique category name.

### documents
Stores uploaded document metadata.

- id – Primary key.
- title – Document title.
- original_filename – Original uploaded filename.
- storage_key – Unique storage identifier.
- mime_type – Document MIME type.
- size_bytes – Document size.
- sha256 – Document integrity hash.
- owner_id – References users(id).
- category_id – References categories(id).
- created_at – Creation timestamp.
- updated_at – Last modification timestamp.

### permissions
Controls document access.

- id – Primary key.
- document_id – References documents(id).
- user_id – References users(id).
- granted_by – References users(id).
- permission_type – Read or edit permission.
- created_at – Permission creation timestamp.

### audit_logs
Maintains security and activity records.

- id – Primary key.
- actor_id – References users(id).
- document_id – References documents(id).
- action – Activity performed.
- result – Operation result.
- ip_address – Request IP address.
- event_data – Additional event information in JSON format.
- previous_hash – Previous audit record hash.
- event_hash – Current audit record hash.
- created_at – Event timestamp.

## 4. Database Setup Instructions

### Step 1: Start MySQL Server

Start your MySQL service using Windows Services or MySQL Workbench.

### Step 2: Open MySQL Command Line

Open PowerShell or Command Prompt and execute:

```bash
mysql -u root -p
```

Enter your MySQL password.

### Step 3: Execute Database Schema

Navigate to the TrustVault project directory.

Run the following command from PowerShell:

```powershell
mysql -u root -p < database/schema.sql
```

Enter your MySQL password when prompted.

This command creates the trustvault database, its tables, relationships, and default document categories.

### Step 4: Verify Database Creation

Log in to MySQL:

```sql
USE trustvault;
SHOW TABLES;
```

Expected tables:

- users
- categories
- documents
- permissions
- audit_logs

### Step 5: Verify Table Structure

To inspect the table structure:

```sql
DESCRIBE users;
DESCRIBE categories;
DESCRIBE documents;
DESCRIBE permissions;
DESCRIBE audit_logs;
```

### Step 6: Verify Default Categories

Execute:

```sql
SELECT * FROM categories;
```

Default categories:

- Personal
- Finance
- Legal
- HR
- Technical
- Other

## 5. Database Relationships

The database uses primary keys and foreign keys to maintain referential integrity.

- users.id → documents.owner_id
- categories.id → documents.category_id
- documents.id → permissions.document_id
- users.id → permissions.user_id
- users.id → permissions.granted_by
- users.id → audit_logs.actor_id
- documents.id → audit_logs.document_id

## 6. Security Considerations

- User passwords are stored as password hashes.
- Email addresses must be unique.
- User roles are restricted to admin, owner, and viewer.
- Document permissions are restricted to read and edit.
- Foreign keys maintain relationships between records.
- Audit logs maintain security activity information.
- Database credentials should be stored securely in environment variables.
- Database access should follow the principle of least privilege.

## 7. Troubleshooting

**Problem: Access denied**

Check your MySQL username and password.

**Problem: Database does not exist**

Execute the schema.sql file again.

**Problem: Table already exists**

The database creation script uses CREATE TABLE statements. Avoid repeatedly executing it against an existing database without checking the current schema.

**Problem: Foreign key constraint error**

Verify that referenced tables and columns exist and use compatible data types.

## 8. Conclusion

The TrustVault database provides structured storage for user accounts, document metadata, access permissions, categories, and audit logs.

The MySQL schema establishes relationships between these entities and supports the application's secure document-sharing functionality.