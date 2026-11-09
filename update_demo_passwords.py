
import os

from app import create_app
from extensions import db
from models.user import User

app = create_app()

accounts = [
    {
        "email": os.getenv("SEED_OWNER_EMAIL"),
        "password": os.getenv("SEED_OWNER_PASSWORD"),
    },
    {
        "email": os.getenv("SEED_VIEWER_EMAIL"),
        "password": os.getenv("SEED_VIEWER_PASSWORD"),
    },
]

with app.app_context():
    for account in accounts:
        email = account["email"]
        password = account["password"]

        if not email or not password or len(password) < 12:
            raise ValueError("Check your .env credentials.")

        email = email.strip().lower()

        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"Account not found: {email}")
            continue

        user.set_password(password)
        print(f"Password updated for: {email}")

    db.session.commit()

print("Demo password update completed.")
