from extensions import db


class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    granted_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    permission_type = db.Column(
        db.String(10),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    __table_args__ = (
        db.UniqueConstraint(
            "document_id",
            "user_id",
            name="uq_document_user_permission"
        ),
        db.CheckConstraint(
            "permission_type IN ('read', 'edit')",
            name="chk_permission_type"
        ),
    )

    document = db.relationship(
        "Document",
        back_populates="permissions"
    )

    user = db.relationship(
        "User",
        foreign_keys=[user_id]
    )

    grantor = db.relationship(
        "User",
        foreign_keys=[granted_by]
    )

    def __repr__(self):
        return f"<Permission {self.permission_type}>"