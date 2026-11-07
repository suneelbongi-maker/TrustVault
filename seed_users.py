import os

from app import create_app
from extensions import db
from models.user import User

app = create_app()

accounts = [
    {
        "name": "TrustVault Admin",
        "email": os.getenv("SEED_ADMIN_EMAIL"),
        "password": os.getenv("SEED_ADMIN_PASSWORD"),
        "role": "admin",
    },
    {
        "name": "Document Owner",
        "email": os.getenv("SEED_OWNER_EMAIL"),
        "password": os.getenv("SEED_OWNER_PASSWORD"),
        "role": "owner",
    },
    {
        "name": "Document Viewer",
        "email": os.getenv("SEED_VIEWER_EMAIL"),
        "password": os.getenv("SEED_VIEWER_PASSWORD"),
        "role": "viewer",
    },
]

with app.app_context():
    for account in accounts:
        if not account["email"] or not account["password"]:
            raise ValueError("Missing seed account credentials in .env")

        if len(account["password"]) < 12:
            raise ValueError("Seed passwords must be at least 12 characters.")

        email = account["email"].strip().lower()
        existing = User.query.filter_by(email=email).first()

        if existing:
            print(f"Account already exists: {email}")
            continue

        user = User(
            name=account["name"],
            email=email,
            role=account["role"],
            is_active=True,
        )
        user.set_password(account["password"])
        db.session.add(user)

    db.session.commit()
    print("Demo accounts created successfully.")
