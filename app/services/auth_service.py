from app.models.usuario import User
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

def registrar_usuario(nombre, correo, password, tipo):
    """Registrar un nuevo usuario"""
    if User.query.filter_by(correo=correo).first():
        return False, "El correo ya está registrado."

    hashed = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

    user = User(
        nombre=nombre,
        correo=correo,
        password=hashed,
        tipo=tipo   
    
    )

    db.session.add(user)
    db.session.commit()

    return True, "Usuario registrado con éxito."
    
def validar_login(correo, password):
    user = User.query.filter_by(correo=correo).first()
    if not user:
        return False, "Usuario no encontrado"
    if not check_password_hash(user.password, password):
        return False, "Contraseña incorrecta"
    return True, user