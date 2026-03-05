from flask import Blueprint, render_template, session, redirect, url_for
from app import db
from app.models.mascota import Mascota
from functools import wraps

mascota_bp = Blueprint("mascota", __name__, url_prefix="/mascotas")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

@mascota_bp.route("/", methods=["GET"])
@login_required
def ver_mascotas():
    # Aquí podrías traer las mascotas del usuario
    # Ejemplo:
    # mascotas = Mascota.query.filter_by(dueno_id=session["user_id"]).all()
    return render_template("mascotas.html")  # Tu template de dashboard