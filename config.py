import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is missing.")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost/trustvault"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    )

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    REMEMBER_COOKIE_SAMESITE = "Lax"

    WTF_CSRF_ENABLED = True
    # Document storage configuration
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "uploads"
    )

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    # Rate limiter storage configuration
    RATELIMIT_STORAGE_URI = os.getenv(
    "RATELIMIT_STORAGE_URI",
    "memory://"
)
