from flask import Blueprint, render_template, session, redirect, url_for, request, flash, Response
from app import db
from app.models.mascota import Mascota
from app.models.historial_medico import HistorialMedico
from functools import wraps

mascota_bp = Blueprint("mascota", __name__, url_prefix="/mascotas")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión primero.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@mascota_bp.route('/registro_mascota', methods=['GET', 'POST'])
@login_required
def registro_mascota():
    if request.method == 'POST':
        if session.get('tipo') not in ('dueno', 'veterinario'):
            flash("No tienes permiso para registrar mascotas.", "error")
            return redirect(url_for('auth.home'))

        nombre = request.form.get('nombre')
        especie = request.form.get('especie')
        raza = request.form.get('raza')
        historial_text = request.form.get('historial')
        edad = request.form.get('edad')

        if not nombre or not especie or not edad:
            flash("Nombre, especie y edad son obligatorios", "error")
            return redirect(url_for('mascota.registro_mascota'))

        try:
            edad_int = int(edad)
        except (ValueError, TypeError):
            flash("Edad debe ser un número entero", "error")
            return redirect(url_for('mascota.registro_mascota'))

        dueno_id = session.get('user_id')
        if not dueno_id:
            flash("No se pudo identificar al dueño. Inicia sesión nuevamente.", "error")
            return redirect(url_for('auth.login'))

        nueva_mascota = Mascota(
            nombre=nombre,
            especie=especie,
            raza=raza,
            edad=edad_int,
            dueno_id=dueno_id
        )

        try:
            # Procesar imagen si fue subida
            imagen_file = request.files.get('imagen')
            if imagen_file and imagen_file.filename:
                nueva_mascota.imagen = imagen_file.read()
                nueva_mascota.imagen_mimetype = imagen_file.mimetype

            db.session.add(nueva_mascota)
            # si el usuario envió información de historial, crear el registro
            if historial_text:
                nueva_historial = HistorialMedico(descripcion=historial_text, mascota=nueva_mascota)
                db.session.add(nueva_historial)

            db.session.commit()
            return redirect(url_for('mascota.ver_mascotas'))
        except Exception as e:
            db.session.rollback()
            flash("Ocurrió un error al registrar la mascota. Intenta de nuevo.", "error")
            return redirect(url_for('mascota.registro_mascota'))

    return render_template('registro_mascota.html')


@mascota_bp.route('/<int:mascota_id>/imagen')
def mascota_imagen(mascota_id):
    m = Mascota.query.get_or_404(mascota_id)
    if not m.imagen:
        # No image stored
        return ('', 404)
    return Response(m.imagen, mimetype=m.imagen_mimetype)


@mascota_bp.route('/', methods=['GET'])
@login_required
def ver_mascotas():
    mascotas = Mascota.query.filter_by(dueno_id=session.get('user_id')).all()
    return render_template('mascotas.html', mascotas=mascotas)


@mascota_bp.route('/<int:mascota_id>/eliminar', methods=['POST'])
@login_required
def eliminar_mascota(mascota_id):
    m = Mascota.query.get_or_404(mascota_id)
    # Only allow owner or veterinario to delete
    user_id = session.get('user_id')
    tipo = session.get('tipo')
    if not user_id:
        flash('Debes iniciar sesión para eliminar mascotas.', 'error')
        return redirect(url_for('auth.login'))

    if not (tipo == 'veterinario' or user_id == m.dueno_id):
        flash('No tienes permiso para eliminar esta mascota.', 'error')
        return redirect(url_for('mascota.ver_mascotas'))

    try:
        db.session.delete(m)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al eliminar la mascota.', 'error')

    return redirect(url_for('mascota.ver_mascotas'))