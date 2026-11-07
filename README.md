# TrustVault - Phase 1

Flask + MySQL authentication starter for the Snovasys TrustVault challenge.

## Requirements

* Python 3.11+
* MySQL Server

## Setup (Windows PowerShell)

```powershell
cd TrustVault
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, set a strong `SECRET\_KEY`, and update the MySQL
password in `DATABASE\_URL`. Set unique demo passwords of at least 12 characters.

Generate a secret key:

```powershell
python -c "import secrets; print(secrets.token\_hex(32))"
```

Run `database/schema.sql` in MySQL Workbench, then:

```powershell
python seed\_users.py
python app.py
```

Open http://127.0.0.1:5000

Run tests:

```powershell
pytest -v
```

## Important

* `.env` is ignored by Git. Never commit credentials.
* `SESSION\_COOKIE\_SECURE=False` is for local HTTP development only. Set it to
`True` behind HTTPS in production.
* The `/admin` route demonstrates role checks. Document-level authorization,
private file storage, audit hash-chain verification, and deployment hardening
are not implemented in this Phase 1 starter.
* Do not use Flask's development server or `debug=True` in production.

