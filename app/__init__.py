from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")  
    app.config["SECRET_KEY"] = "clave_super_secreta"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.models.usuario import User
    from app.models.dueno import Dueno
    from app.models.veterinario import Veterinario
    from app.models.mascota import Mascota
    from app.models.consulta import Consulta

    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    from app.routes.mascota_routes import mascota_bp
    app.register_blueprint(mascota_bp)

    return app