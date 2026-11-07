from extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        primary_key=True
    )

    actor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True
    )

    action = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(20), nullable=False)
    ip_address = db.Column(db.String(45))

    event_data = db.Column(db.JSON)
    previous_hash = db.Column(db.String(64))

    event_hash = db.Column(
        db.String(64),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    actor = db.relationship(
        "User",
        foreign_keys=[actor_id]
    )

    document = db.relationship(
        "Document",
        back_populates="audit_logs"
    )

    def __repr__(self):
        return f"<AuditLog {self.action}>"