from extensions import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(
        db.String(255),
        nullable=False
    )
    storage_key = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )
    mime_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.BigInteger, nullable=False)
    sha256 = db.Column(db.String(64))

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    owner = db.relationship(
        "User",
        foreign_keys=[owner_id]
    )

    category = db.relationship(
        "Category",
        back_populates="documents"
    )

    permissions = db.relationship(
        "Permission",
        back_populates="document",
        cascade="all, delete-orphan"
    )

    audit_logs = db.relationship(
        "AuditLog",
        back_populates="document"
    )

    def __repr__(self):
        return f"<Document {self.title}>"