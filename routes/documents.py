
import os
import uuid
import hashlib
import json
import mimetypes

from pathlib import Path

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, abort, send_file
)

from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from extensions import db
from models import Document, Category, Permission, AuditLog
from security.decorators import role_required


documents = Blueprint("documents", __name__)

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "txt", "png", "jpg", "jpeg"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# PATH-TRAVERSAL PROTECTION
def get_safe_storage_path(storage_key):

    upload_root = Path(
        current_app.config["UPLOAD_FOLDER"]
    ).resolve()

    # Reject filenames containing directory separators
    if (
        not storage_key
        or Path(storage_key).name != storage_key
        or "/" in storage_key
        or "\\" in storage_key
    ):
        abort(404)

    file_path = (upload_root / storage_key).resolve()

    # Ensure the resolved path stays inside uploads
    try:
        file_path.relative_to(upload_root)

    except ValueError:
        abort(404)

    return file_path


def create_audit_log(action, result, document=None):

    previous = AuditLog.query.order_by(
        AuditLog.id.desc()
    ).first()

    previous_hash = previous.event_hash if previous else None

    event_data = {
        "filename": document.original_filename if document else None
    }

    audit_data = {
        "actor_id": current_user.id,
        "document_id": document.id if document else None,
        "action": action,
        "result": result,
        "ip_address": request.remote_addr,
        "event_data": event_data,
        "previous_hash": previous_hash
    }

    serialized = json.dumps(
        audit_data,
        sort_keys=True,
        separators=(",", ":")
    )

    event_hash = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    log = AuditLog(
        actor_id=current_user.id,
        document_id=document.id if document else None,
        action=action,
        result=result,
        ip_address=request.remote_addr,
        event_data=event_data,
        previous_hash=previous_hash,
        event_hash=event_hash
    )

    db.session.add(log)


@documents.route("/documents")
@login_required
def document_list():

    if current_user.role == "admin":

        document_list = Document.query.order_by(
            Document.created_at.desc()
        ).all()

    else:

        document_list = Document.query.filter(
            or_(
                Document.owner_id == current_user.id,
                Document.permissions.any(
                    Permission.user_id == current_user.id
                )
            )
        ).order_by(
            Document.created_at.desc()
        ).all()

    categories = Category.query.order_by(
        Category.name
    ).all()

    return render_template(
        "documents.html",
        documents=document_list,
        categories=categories,
        user=current_user
    )


@documents.route("/documents/upload", methods=["POST"])
@login_required
@role_required("admin", "owner")
def upload_document():

    title = request.form.get("title", "").strip()
    uploaded_file = request.files.get("file")
    category_id = request.form.get("category_id", "").strip()

    if not title:
        flash("Document title is required.", "danger")
        return redirect(url_for("documents.document_list"))

    if not uploaded_file or not uploaded_file.filename:
        flash("Please select a file.", "danger")
        return redirect(url_for("documents.document_list"))

    original_filename = secure_filename(
        uploaded_file.filename
    )

    if not original_filename or not allowed_file(original_filename):
        flash("Unsupported file type.", "danger")
        return redirect(url_for("documents.document_list"))

    uploaded_file.stream.seek(0, os.SEEK_END)
    file_size = uploaded_file.stream.tell()
    uploaded_file.stream.seek(0)

    if file_size == 0:
        flash("Empty files are not allowed.", "danger")
        return redirect(url_for("documents.document_list"))

    if file_size > current_app.config["MAX_CONTENT_LENGTH"]:
        flash("File exceeds the 10 MB limit.", "danger")
        return redirect(url_for("documents.document_list"))

    category = None

    if category_id:
        try:
            category = db.session.get(
                Category, int(category_id)
            )

        except ValueError:
            category = None

        if category is None:
            flash("Invalid document category.", "danger")
            return redirect(url_for("documents.document_list"))

    storage_folder = current_app.config["UPLOAD_FOLDER"]

    os.makedirs(storage_folder, exist_ok=True)

    extension = original_filename.rsplit(".", 1)[1].lower()

    storage_key = f"{uuid.uuid4().hex}.{extension}"

    file_path = os.path.join(
        storage_folder,
        storage_key
    )

    try:

        uploaded_file.save(file_path)

        sha256 = hashlib.sha256()

        with open(file_path, "rb") as stored_file:

            for chunk in iter(
                lambda: stored_file.read(8192), b""
            ):
                sha256.update(chunk)

        mime_type = (
            mimetypes.guess_type(original_filename)[0]
            or "application/octet-stream"
        )

        document = Document(
            title=title,
            original_filename=original_filename,
            storage_key=storage_key,
            mime_type=mime_type,
            size_bytes=file_size,
            sha256=sha256.hexdigest(),
            owner_id=current_user.id,
            category_id=category.id if category else None
        )

        db.session.add(document)
        db.session.flush()

        create_audit_log(
            "document_upload",
            "success",
            document
        )

        db.session.commit()

        flash("Document uploaded successfully!", "success")

    except (OSError, SQLAlchemyError):

        db.session.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        current_app.logger.exception(
            "Document upload failed"
        )

        flash("Document upload failed.", "danger")

    return redirect(url_for("documents.document_list"))


@documents.route("/documents/download/<int:document_id>")
@login_required
def download_document(document_id):

    document = db.session.get(Document, document_id)

    if document is None:
        abort(404)

    # Check whether the current user can download the document
    permitted = (
        current_user.role == "admin"
        or document.owner_id == current_user.id
    )

    # Check shared permissions
    if not permitted:

        permission = Permission.query.filter_by(
            document_id=document.id,
            user_id=current_user.id
        ).first()

        permitted = permission is not None

    # Deny unauthorized downloads
    if not permitted:

        try:

            create_audit_log(
                "document_download",
                "denied",
                document
            )

            db.session.commit()

        except SQLAlchemyError:

            db.session.rollback()

            current_app.logger.exception(
                "Failed to record denied download attempt"
            )

            abort(500)

        abort(403)

    # Get the safely resolved stored file path
    file_path = get_safe_storage_path(
        document.storage_key
    )

    # Check whether the file exists
    if not file_path.is_file():
        abort(404)

    # Record successful download
    try:

        create_audit_log(
            "document_download",
            "success",
            document
        )

        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        current_app.logger.exception(
            "Download audit logging failed"
        )

        abort(500)

    # Send document to authorized user
    return send_file(
        file_path,
        as_attachment=True,
        download_name=document.original_filename
    )
