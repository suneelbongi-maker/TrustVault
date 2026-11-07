
import re
import pytest

from app import create_app
from extensions import db
from models.user import User


@pytest.fixture
def app():
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "csrf-test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "WTF_CSRF_ENABLED": True,
        "WTF_CSRF_CHECK_DEFAULT": True,
        "RATELIMIT_ENABLED": False,
    })

    with application.app_context():
        db.create_all()

        owner = User(
            name="Test Owner",
            email="owner@test.com",
            role="owner"
        )
        owner.set_password("OwnerPassword123!")

        db.session.add(owner)
        db.session.commit()

        yield application

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def get_csrf_token(client):
    response = client.get("/login")

    assert response.status_code == 200

    match = re.search(
        rb'name="csrf_token"[^>]*value="([^"]+)"',
        response.data
    )

    assert match is not None

    return match.group(1).decode()


def login_with_csrf(client):
    token = get_csrf_token(client)

    return client.post(
        "/login",
        data={
            "csrf_token": token,
            "email": "owner@test.com",
            "password": "OwnerPassword123!"
        }
    )


def test_login_rejects_missing_csrf_token(client):
    response = client.post(
        "/login",
        data={
            "email": "owner@test.com",
            "password": "OwnerPassword123!"
        }
    )

    assert response.status_code == 400


def test_login_rejects_invalid_csrf_token(client):
    response = client.post(
        "/login",
        data={
            "csrf_token": "invalid-token",
            "email": "owner@test.com",
            "password": "OwnerPassword123!"
        }
    )

    assert response.status_code == 400


def test_login_accepts_valid_csrf_token(client):
    response = login_with_csrf(client)

    assert response.status_code == 302


def test_logout_rejects_missing_csrf_token(client):
    login_with_csrf(client)

    response = client.post("/logout")

    assert response.status_code == 400


def test_document_upload_rejects_missing_csrf_token(client):
    login_with_csrf(client)

    response = client.post(
        "/documents/upload",
        data={},
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
