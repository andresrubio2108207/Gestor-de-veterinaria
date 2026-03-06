from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión primero.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Debes iniciar sesión primero.", "error")
                return redirect(url_for("auth.login"))

            if session.get("tipo") != role:
                flash("No tienes permiso para acceder aquí.", "error")
                return redirect(url_for("auth.home"))

            return f(*args, **kwargs)
        return wrapper
    return decorator