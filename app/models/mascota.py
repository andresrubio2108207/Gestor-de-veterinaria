from app import db
from datetime import datetime

class Mascota(db.Model):
    __tablename__ = "mascotas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(100))
    edad = db.Column(db.Integer, nullable=False)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    dueno_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    dueno = db.relationship(
        "Dueno",
        back_populates="mascotas"
    )

    consultas = db.relationship(
        "Consulta",
        back_populates="mascota",
        cascade="all, delete-orphan"
    )