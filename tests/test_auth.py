import pytest

from app import create_app
from extensions import db
from models.user import User


@pytest.fixture
def app():
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "WTF_CSRF_ENABLED": False,
        "RATELIMIT_ENABLED": False,
    })

    with application.app_context():
        db.create_all()

        admin = User(name="Admin", email="admin@test.com", role="admin")
        admin.set_password("AdminPassword123!")

        viewer = User(name="Viewer", email="viewer@test.com", role="viewer")
        viewer.set_password("ViewerPassword123!")

        inactive = User(
            name="Inactive",
            email="inactive@test.com",
            role="owner",
            is_active=False,
        )
        inactive.set_password("InactivePassword123!")

        db.session.add_all([admin, viewer, inactive])
        db.session.commit()

        yield application

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_dashboard_requires_login(client):
    response = client.get("/")
    assert response.status_code == 302


def test_successful_login(client):
    response = client.post(
        "/login",
        data={"email": "admin@test.com", "password": "AdminPassword123!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"TrustVault Dashboard" in response.data


def test_wrong_password(client):
    response = client.post(
        "/login",
        data={"email": "admin@test.com", "password": "WrongPassword123!"},
        follow_redirects=True,
    )
    assert b"Invalid email or password" in response.data


def test_viewer_cannot_access_admin(client):
    client.post(
        "/login",
        data={"email": "viewer@test.com", "password": "ViewerPassword123!"},
    )
    response = client.get("/admin")
    assert response.status_code == 403


def test_inactive_user_cannot_login(client):
    response = client.post(
        "/login",
        data={"email": "inactive@test.com", "password": "InactivePassword123!"},
        follow_redirects=True,
    )
    assert b"Invalid email or password" in response.data
 
# Additional TrustVault tests

def test_admin_can_access_admin(client):
    client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "AdminPassword123!"
        }
    )

    response = client.get("/admin")
    assert response.status_code == 200
    assert b"Admin access granted" in response.data


def test_user_password_is_hashed(app):
    with app.app_context():
        user = User.query.filter_by(email="admin@test.com").first()

        assert user.password_hash != "AdminPassword123!"
        assert user.password_hash.startswith("scrypt:")


def test_user_password_verification(app):
    with app.app_context():
        user = User.query.filter_by(email="admin@test.com").first()

        assert user.check_password("AdminPassword123!")
        assert not user.check_password("WrongPassword123!")


def test_user_has_role(app):
    with app.app_context():
        user = User.query.filter_by(email="admin@test.com").first()

        assert user.has_role("admin")
        assert not user.has_role("viewer")


def test_login_email_is_case_insensitive(client):
    response = client.post(
        "/login",
        data={
            "email": "ADMIN@TEST.COM",
            "password": "AdminPassword123!"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"TrustVault Dashboard" in response.data


def test_logout(client):
    client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "AdminPassword123!"
        }
    )

    response = client.post("/logout")

    assert response.status_code == 302

    dashboard = client.get("/")
    assert dashboard.status_code == 302


def test_logout_rejects_get_request(client):
    response = client.get("/logout")
    assert response.status_code == 405
from sqlalchemy.exc import IntegrityError


def test_create_and_retrieve_user(app):
    with app.app_context():
        user = User(
            name="Test User",
            email="testuser@test.com",
            role="owner"
        )
        user.set_password("TestPassword123!")

        db.session.add(user)
        db.session.commit()

        saved_user = User.query.filter_by(
            email="testuser@test.com"
        ).first()

        assert saved_user is not None
        assert saved_user.name == "Test User"
        assert saved_user.role == "owner"


def test_duplicate_email_not_allowed(app):
    with app.app_context():
        user = User(
            name="Duplicate User",
            email="admin@test.com",
            role="viewer"
        )
        user.set_password("TestPassword123!")

        db.session.add(user)

        try:
            db.session.commit()
            assert False, "Duplicate email should not be allowed"
        except IntegrityError:
            db.session.rollback()


def test_user_required_fields(app):
    with app.app_context():
        user = User(
            name="Missing Password",
            email="missing@test.com",
            role="viewer"
        )

        db.session.add(user)

        try:
            db.session.commit()
            assert False, "Password hash should be required"
        except IntegrityError:
            db.session.rollback()



