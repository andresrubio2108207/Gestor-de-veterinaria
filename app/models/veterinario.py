from app import db
from app.models.usuario import User

class Veterinario(User):
    __tablename__ = "veterinarios"

    id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), primary_key=True)

    consultas = db.relationship(
        "Consulta",
        back_populates="veterinario"
    )

    __mapper_args__ = {
        "polymorphic_identity": "veterinario"
    }