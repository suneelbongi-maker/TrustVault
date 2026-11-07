
from extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    documents = db.relationship(
        "Document",
        back_populates="category"
    )

    def __repr__(self):
        return f"<Category {self.name}>"
