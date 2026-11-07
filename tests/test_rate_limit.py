
from app import create_app
from extensions import db


def test_login_rate_limit():
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "WTF_CSRF_ENABLED": False,
        "RATELIMIT_ENABLED": True,
        "RATELIMIT_STORAGE_URI": "memory://",
    })

    with application.app_context():
        db.create_all()

    client = application.test_client()

    try:
        # First five requests should be allowed.
        for _ in range(5):
            response = client.post(
                "/login",
                data={
                    "email": "wrong@test.com",
                    "password": "WrongPassword123!"
                }
            )
            assert response.status_code == 200

        # Sixth request should be rate limited.
        response = client.post(
            "/login",
            data={
                "email": "wrong@test.com",
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == 429

    finally:
        with application.app_context():
            db.session.remove()
            db.drop_all()
