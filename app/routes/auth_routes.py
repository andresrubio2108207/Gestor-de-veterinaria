from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from ..services.auth_service import registrar_usuario, validar_login
from functools import wraps

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET"])
def home_redirect():
    return redirect(url_for("auth.login"))

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
                flash("Debes iniciar sesión primero.")
                return redirect(url_for("auth.login"))

            if session.get("tipo") != role:
                flash("No tienes permiso para acceder aquí.")
                return redirect(url_for("auth.home"))

            return f(*args, **kwargs)
        return wrapper
    return decorator

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo")
        password = request.form.get("password")
        success, user = validar_login(correo, password)
        if success:
            session["user_id"] = user.id
            session["nombre"] = user.nombre
            session["tipo"] = user.tipo
            flash("Has iniciado sesión correctamente.")
            return redirect(url_for("auth.home"))
        flash("Correo o contraseña incorrectos.")
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        password = request.form.get("password")
        tipo = request.form.get("tipo")
        success, msg = registrar_usuario(nombre, correo, password, tipo)
        flash(msg)
        return redirect(url_for("auth.login")) if success else redirect(url_for("auth.register"))
    return render_template("register.html")

@auth_bp.route("/home")
@login_required
def home():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("home.html")

@auth_bp.route("/mascotas")
@role_required("dueno")   
def mascotas():
    return render_template("mascotas.html")

@auth_bp.route("/consultas")
@role_required("veterinario")
def consultas():
    return render_template("consultas.html")

@auth_bp.route("/historial")
def historial():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("historial.html")

@auth_bp.route("/veterinarios")
def veterinarios():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("veterinarios.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))