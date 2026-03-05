from app import db

class User(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20))
    

    __mapper_args__ = {
        "polymorphic_on": tipo,
        "polymorphic_identity": "usuario"
    }

    def __repr__(self):
        return f'<User {self.username}>'