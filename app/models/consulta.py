from app import db
from datetime import datetime

class Consulta(db.Model):
    __tablename__ = "consultas"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    motivo = db.Column(db.Text, nullable=False)
    diagnostico = db.Column(db.Text)
    tratamiento = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default="agendada")

    mascota_id = db.Column(
        db.Integer,
        db.ForeignKey("mascotas.id"),
        nullable=False
    )

    veterinario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    mascota = db.relationship(
        "Mascota",
        back_populates="consultas"
    )

    veterinario = db.relationship(
        "Veterinario",
        back_populates="consultas"
    )