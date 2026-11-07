
import io
import pytest

from app import create_app
from extensions import db
from models.user import User
from models.category import Category
from models.document import Document
from models.permission import Permission
from models.audit_log import AuditLog
from pathlib import Path


@pytest.fixture
def document_app(tmp_path):
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "WTF_CSRF_ENABLED": False,
        "RATELIMIT_ENABLED": False,
        "UPLOAD_FOLDER": str(tmp_path),
        "MAX_CONTENT_LENGTH": 10 * 1024 * 1024,
    })

    with application.app_context():
        db.create_all()

        admin = User(
            name="Admin",
            email="admin@test.com",
            role="admin"
        )
        admin.set_password("AdminPassword123!")

        owner = User(
            name="Owner",
            email="owner@test.com",
            role="owner"
        )
        owner.set_password("OwnerPassword123!")

        viewer = User(
            name="Viewer",
            email="viewer@test.com",
            role="viewer"
        )
        viewer.set_password("ViewerPassword123!")

        other_owner = User(
            name="Other Owner",
            email="other@test.com",
            role="owner"
        )
        other_owner.set_password("OtherPassword123!")

        category = Category(name="Reports")

        db.session.add_all([
            admin, owner, viewer, other_owner, category
        ])
        db.session.commit()

        yield application

        db.session.remove()
        db.drop_all()


@pytest.fixture
def document_client(document_app):
    return document_app.test_client()


def login(client, email, password):
    return client.post(
        "/login",
        data={
            "email": email,
            "password": password
        },
        follow_redirects=True
    )


def upload_file(client, filename="report.pdf", content=b"Test document"):
    return client.post(
        "/documents/upload",
        data={
            "title": "Test Report",
            "category_id": "1",
            "file": (
                io.BytesIO(content),
                filename
            )
        },
        content_type="multipart/form-data",
        follow_redirects=False
    )


def test_admin_can_upload_document(document_client):
    login(
        document_client,
        "admin@test.com",
        "AdminPassword123!"
    )

    response = upload_file(document_client)

    assert response.status_code == 302

    with document_client.application.app_context():
        assert Document.query.count() == 1
        assert AuditLog.query.filter_by(
            action="document_upload",
            result="success"
        ).count() == 1


def test_owner_can_upload_document(document_client):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    response = upload_file(document_client)

    assert response.status_code == 302

    with document_client.application.app_context():
        assert Document.query.count() == 1


def test_viewer_cannot_upload_document(document_client):
    login(
        document_client,
        "viewer@test.com",
        "ViewerPassword123!"
    )

    response = upload_file(document_client)

    assert response.status_code == 403

    with document_client.application.app_context():
        assert Document.query.count() == 0


def test_unsupported_file_is_rejected(document_client):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    response = upload_file(
        document_client,
        filename="malware.exe"
    )

    assert response.status_code == 302

    with document_client.application.app_context():
        assert Document.query.count() == 0


def test_empty_file_is_rejected(document_client):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    response = upload_file(
        document_client,
        filename="empty.pdf",
        content=b""
    )

    assert response.status_code == 302

    with document_client.application.app_context():
        assert Document.query.count() == 0


def test_file_over_10mb_is_rejected(document_client):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    large_content = b"A" * (10 * 1024 * 1024 + 1)

    response = upload_file(
        document_client,
        filename="large.pdf",
        content=large_content
    )

    assert response.status_code == 413

    with document_client.application.app_context():
        assert Document.query.count() == 0


def test_owner_can_download_own_document(document_client):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    upload_file(document_client)

    with document_client.application.app_context():
        document = Document.query.first()
        document_id = document.id

    response = document_client.get(
        f"/documents/download/{document_id}"
    )

    assert response.status_code == 200
    assert response.data == b"Test document"

    with document_client.application.app_context():
        assert AuditLog.query.filter_by(
            action="document_download",
            result="success"
        ).count() == 1


def test_other_user_cannot_download_private_document(document_client):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    upload_file(document_client)

    with document_client.application.app_context():
        document = Document.query.first()
        document_id = document.id

    document_client.post("/logout")

    login(
        document_client,
        "other@test.com",
        "OtherPassword123!"
    )

    response = document_client.get(
        f"/documents/download/{document_id}"
    )

    assert response.status_code == 403


def test_admin_can_download_document(document_client):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    upload_file(document_client)

    with document_client.application.app_context():
        document_id = Document.query.first().id

    document_client.post("/logout")

    login(
        document_client,
        "admin@test.com",
        "AdminPassword123!"
    )

    response = document_client.get(
        f"/documents/download/{document_id}"
    )

    assert response.status_code == 200


def test_shared_user_can_download_document(document_client):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    upload_file(document_client)

    with document_client.application.app_context():
        document = Document.query.first()

        viewer = User.query.filter_by(
            email="viewer@test.com"
        ).first()

        owner = User.query.filter_by(
            email="owner@test.com"
        ).first()

        permission = Permission(
            document_id=document.id,
            user_id=viewer.id,
            granted_by=owner.id,
            permission_type="read"
        )

        db.session.add(permission)
        db.session.commit()

        document_id = document.id

    document_client.post("/logout")

    login(
        document_client,
        "viewer@test.com",
        "ViewerPassword123!"
    )

    response = document_client.get(
        f"/documents/download/{document_id}"
    )

    assert response.status_code == 200
    assert response.data == b"Test document"


def test_revoked_permission_denies_download(document_client):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    upload_file(document_client)

    with document_client.application.app_context():
        document = Document.query.first()

        viewer = User.query.filter_by(
            email="viewer@test.com"
        ).first()

        owner = User.query.filter_by(
            email="owner@test.com"
        ).first()

        permission = Permission(
            document_id=document.id,
            user_id=viewer.id,
            granted_by=owner.id,
            permission_type="read"
        )

        db.session.add(permission)
        db.session.commit()

        document_id = document.id

        db.session.delete(permission)
        db.session.commit()

    document_client.post("/logout")

    login(
        document_client,
        "viewer@test.com",
        "ViewerPassword123!"
    )

    response = document_client.get(
        f"/documents/download/{document_id}"
    )

    assert response.status_code == 403
    
# ==========================================
# PATH-TRAVERSAL SECURITY TESTS
# ==========================================

@pytest.mark.parametrize(
    "malicious_storage_key",
    [
        "../outside.pdf",
        r"..\outside.pdf",
        r"C:\outside\secret.pdf",
        "/outside/secret.pdf",
    ]
)
def test_download_rejects_malicious_storage_paths(
    document_client,
    malicious_storage_key
):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    upload_file(document_client)

    with document_client.application.app_context():

        document = Document.query.first()

        document.storage_key = malicious_storage_key

        db.session.commit()

        document_id = document.id

    response = document_client.get(
        f"/documents/download/{document_id}"
    )

    assert response.status_code == 404


def test_download_rejects_symlink_outside_upload_folder(
    document_client
):
    login(
        document_client,
        "owner@test.com",
        "OwnerPassword123!"
    )

    upload_file(document_client)

    upload_root = Path(
        document_client.application.config["UPLOAD_FOLDER"]
    ).resolve()

    outside_file = (
        upload_root.parent /
        f"{upload_root.name}_outside_secret.txt"
    )

    link_name = "outside-link.pdf"
    link_path = upload_root / link_name

    original_file = None

    try:
        with document_client.application.app_context():

            document = Document.query.first()

            original_file = upload_root / document.storage_key

            original_file.unlink()

            document.storage_key = link_name

            db.session.commit()

            document_id = document.id

        outside_file.write_text(
            "Private external content",
            encoding="utf-8"
        )

        try:
            link_path.symlink_to(outside_file)

        except (OSError, NotImplementedError):
            pytest.skip(
                "Symbolic links are not supported "
                "or permitted on this system."
            )

        response = document_client.get(
            f"/documents/download/{document_id}"
        )

        assert response.status_code == 404

    finally:

        if link_path.is_symlink():
            link_path.unlink()

        if outside_file.exists():
            outside_file.unlink()

