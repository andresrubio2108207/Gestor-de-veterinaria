from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'owner' or 'vet'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pets = db.relationship('Pet', back_populates='owner', lazy=True)
    consultations_as_vet = db.relationship(
        'Consultation', foreign_keys='Consultation.vet_id', lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_owner(self):
        return self.role == 'owner'

    def is_vet(self):
        return self.role == 'vet'

    def __repr__(self):
        return f'<User {self.username}>'


class Pet(db.Model):
    __tablename__ = 'pets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    species = db.Column(db.String(80), nullable=False)
    breed = db.Column(db.String(80))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship('User', back_populates='pets')
    consultations = db.relationship('Consultation', back_populates='pet', lazy=True)

    def __repr__(self):
        return f'<Pet {self.name}>'


class Consultation(db.Model):
    __tablename__ = 'consultations'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pendiente')  # 'pendiente' or 'atendida'
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    vet_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pet = db.relationship('Pet', back_populates='consultations')
    vet = db.relationship('User', foreign_keys=[vet_id])
    medical_record = db.relationship(
        'MedicalRecord', back_populates='consultation', uselist=False, lazy=True
    )

    def __repr__(self):
        return f'<Consultation {self.id} - {self.status}>'


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    observations = db.Column(db.Text)
    consultation_id = db.Column(
        db.Integer, db.ForeignKey('consultations.id'), unique=True, nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    consultation = db.relationship('Consultation', back_populates='medical_record')

    def __repr__(self):
        return f'<MedicalRecord {self.id}>'
