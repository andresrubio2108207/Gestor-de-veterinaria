from functools import wraps
from flask import session, redirect, url_for, flash
from models.usuario import User

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Debes iniciar sesión.")
                return redirect(url_for("auth.login"))

            user = User.query.get(session["user_id"])

            if not user or user.tipo != role:
                flash("No tienes permiso para acceder aquí.")
                return redirect(url_for("auth.home"))

            return f(*args, **kwargs)
        return wrapper
    return decorator