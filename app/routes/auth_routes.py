from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from sqlalchemy import text
from ..services.auth_service import registrar_usuario, validar_login
from app import db
from app.models.consulta import Consulta
from app.models.mascota import Mascota
from app.models.usuario import User
from app.models.veterinario import Veterinario
from app.utils.decorators import login_required, role_required


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def home_redirect():
    return redirect(url_for("auth.login"))


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


@auth_bp.route("/consultas", methods=["GET", "POST"])
@login_required
def consultas():
    user_id = session.get("user_id")
    tipo_usuario = session.get("tipo")
    ahora = datetime.now()

    mascotas_usuario = []
    if tipo_usuario == "dueno":
        mascotas_usuario = (
            Mascota.query
            .filter_by(dueno_id=user_id)
            .order_by(Mascota.nombre.asc())
            .all()
        )

    if request.method == "POST":
        if tipo_usuario != "dueno":
            flash("Solo los dueños pueden agendar citas.", "error")
            return redirect(url_for("auth.consultas"))

        mascota_id = request.form.get("mascota_id")
        fecha_cita = request.form.get("fecha_cita")
        hora_cita = request.form.get("hora_cita")
        tipo_consulta = request.form.get("tipo", "General").strip()
        modalidad = request.form.get("modalidad", "No definida").strip()
        mensaje = request.form.get("mensaje", "").strip()

        if not mascota_id or not fecha_cita or not hora_cita or not mensaje:
            flash("Completa todos los campos obligatorios para agendar la cita.", "error")
            return redirect(url_for("auth.consultas"))

        mascota = Mascota.query.filter_by(id=mascota_id, dueno_id=user_id).first()
        if not mascota:
            flash("La mascota seleccionada no es válida para tu cuenta.", "error")
            return redirect(url_for("auth.consultas"))

        veterinario_disponible = Veterinario.query.first()
        if not veterinario_disponible:
            usuario_veterinario = User.query.filter_by(tipo="veterinario").first()
            if usuario_veterinario:
                try:
                    db.session.execute(
                        text("INSERT INTO veterinarios (id) VALUES (:id)"),
                        {"id": usuario_veterinario.id}
                    )
                    db.session.commit()
                    veterinario_disponible = Veterinario.query.filter_by(id=usuario_veterinario.id).first()
                except Exception:
                    db.session.rollback()

        if not veterinario_disponible:
            flash("No hay veterinarios disponibles para agendar la cita.", "error")
            return redirect(url_for("auth.consultas"))

        try:
            fecha_programada = datetime.strptime(f"{fecha_cita} {hora_cita}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash("La fecha u hora de la cita no tiene un formato válido.", "error")
            return redirect(url_for("auth.consultas"))

        if fecha_programada <= ahora:
            flash("Solo puedes agendar citas en fecha y hora futuras.", "error")
            return redirect(url_for("auth.consultas"))

        motivo = f"[{tipo_consulta} - {modalidad}] {mensaje}"
        nueva_consulta = Consulta(
            fecha=fecha_programada,
            motivo=motivo,
            mascota_id=mascota.id,
            veterinario_id=veterinario_disponible.id
        )

        try:
            db.session.add(nueva_consulta)
            db.session.commit()
            flash("Cita agregada exitosamente.", "success")
        except Exception:
            db.session.rollback()
            flash("Ocurrió un error al agendar la cita.", "error")

        return redirect(url_for("auth.consultas"))

    if tipo_usuario == "dueno":
        citas = (
            Consulta.query
            .join(Mascota)
            .filter(
                Mascota.dueno_id == user_id,
                Consulta.fecha >= ahora,
                Consulta.estado == "agendada"
            )
            .order_by(Consulta.fecha.asc())
            .all()
        )
        citas_historial = (
            Consulta.query
            .join(Mascota)
            .filter(
                Mascota.dueno_id == user_id,
                ((Consulta.fecha < ahora) | (Consulta.estado == "cancelada"))
            )
            .order_by(Consulta.fecha.desc())
            .all()
        )
    elif tipo_usuario == "veterinario":
        citas = (
            Consulta.query
            .filter(
                Consulta.veterinario_id == user_id,
                Consulta.fecha >= ahora,
                Consulta.estado == "agendada"
            )
            .order_by(Consulta.fecha.asc())
            .all()
        )
        citas_historial = (
            Consulta.query
            .filter(
                Consulta.veterinario_id == user_id,
                ((Consulta.fecha < ahora) | (Consulta.estado == "cancelada"))
            )
            .order_by(Consulta.fecha.desc())
            .all()
        )
    else:
        citas = []
        citas_historial = []

    return render_template(
        "consultas.html",
        citas=citas,
        citas_historial=citas_historial,
        mascotas_usuario=mascotas_usuario,
        es_dueno=(tipo_usuario == "dueno")
    )


@auth_bp.route("/consultas/<int:consulta_id>/cancelar", methods=["POST"])
@login_required
def cancelar_consulta(consulta_id):
    user_id = session.get("user_id")
    tipo_usuario = session.get("tipo")

    consulta = Consulta.query.get_or_404(consulta_id)

    if consulta.estado == "cancelada":
        flash("Esta cita ya está cancelada.", "info")
        return redirect(url_for("auth.consultas"))

    if consulta.fecha < datetime.now():
        flash("No puedes cancelar una cita pasada.", "error")
        return redirect(url_for("auth.consultas"))

    if tipo_usuario == "dueno":
        mascota = Mascota.query.filter_by(id=consulta.mascota_id, dueno_id=user_id).first()
        if not mascota:
            flash("No tienes permiso para cancelar esta cita.", "error")
            return redirect(url_for("auth.consultas"))
    elif tipo_usuario == "veterinario":
        if consulta.veterinario_id != user_id:
            flash("No tienes permiso para cancelar esta cita.", "error")
            return redirect(url_for("auth.consultas"))
    else:
        flash("No tienes permiso para cancelar esta cita.", "error")
        return redirect(url_for("auth.consultas"))

    try:
        consulta.estado = "cancelada"
        db.session.commit()
        flash("Cita cancelada exitosamente.", "success")
    except Exception:
        db.session.rollback()
        flash("Ocurrió un error al cancelar la cita.", "error")

    return redirect(url_for("auth.consultas"))


@auth_bp.route("/galeria")
def galeria():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("galeria.html")


@auth_bp.route("/veterinarios")
def veterinarios():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("veterinarios.html")


@auth_bp.route("/historial")
def historial():
    return redirect(url_for("auth.galeria"))


@auth_bp.route("/servicios")
def servicios():
    return redirect(url_for("auth.veterinarios"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
