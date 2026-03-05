from app import db
from datetime import datetime

class HistorialMedico(db.Model):
    __tablename__ = "historial_medico"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.Text, nullable=False)
    diagnostico = db.Column(db.Text)
    tratamiento = db.Column(db.Text)

    mascota_id = db.Column(db.Integer, db.ForeignKey("mascotas.id"), nullable=False)
    mascota = db.relationship("Mascota", back_populates="historial")