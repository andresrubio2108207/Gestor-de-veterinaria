from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    secret_key = os.getenv("SECRET_KEY")
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL no esta configurada.")

    app.config["SECRET_KEY"] = secret_key or "dev-only-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    

    from app.models.usuario import User
    from app.models.dueno import Dueno
    from app.models.veterinario import Veterinario
    from app.models.mascota import Mascota
    from app.models.historial_medico import HistorialMedico
    from app.models.consulta import Consulta
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(auth_bp)
    from app.routes.mascota_routes import mascota_bp
    app.register_blueprint(mascota_bp)

    return app