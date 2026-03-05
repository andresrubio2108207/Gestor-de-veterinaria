from app import db
from app.models.usuario import User

class Dueno(User):
    __tablename__ = "duenos"

    id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), primary_key=True)

    mascotas = db.relationship(
        "Mascota",
        back_populates="dueno",
        cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": "dueno"
    }