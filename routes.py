from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app import db
from models import User, Pet, Consultation, MedicalRecord

main = Blueprint('main', __name__)


# ---------------------------------------------------------------------------
# Access-control decorators
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated


def owner_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('main.login'))
        if session.get('role') != 'owner':
            flash('Acceso restringido a dueños de mascotas.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


def vet_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('main.login'))
        if session.get('role') != 'vet':
            flash('Acceso restringido a veterinarios.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@main.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    if session.get('role') == 'owner':
        return redirect(url_for('main.owner_dashboard'))
    if session.get('role') == 'vet':
        return redirect(url_for('main.vet_dashboard'))
    return redirect(url_for('main.login'))


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', '')

        if not all([username, email, password, confirm_password, role]):
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('auth/register.html')

        if role not in ('owner', 'vet'):
            flash('Rol inválido.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado.', 'danger')
            return render_template('auth/register.html')

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Cuenta creada correctamente. Inicia sesión.', 'success')
        return redirect(url_for('main.login'))

    return render_template('auth/register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Usuario y contraseña son obligatorios.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Usuario o contraseña incorrectos.', 'danger')
            return render_template('auth/login.html')

        session['user_id'] = user.id
        session['role'] = user.role
        session['username'] = user.username
        flash(f'Bienvenido, {user.username}!', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')


@main.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('main.login'))


# ---------------------------------------------------------------------------
# Owner routes
# ---------------------------------------------------------------------------

@main.route('/owner/dashboard')
@owner_required
def owner_dashboard():
    user = User.query.get(session['user_id'])
    pending = (
        Consultation.query
        .join(Pet)
        .filter(Pet.owner_id == user.id, Consultation.status == 'pendiente')
        .order_by(Consultation.date)
        .all()
    )
    return render_template('owner/dashboard.html', user=user, pending=pending)


@main.route('/owner/pets/add', methods=['GET', 'POST'])
@owner_required
def add_pet():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        species = request.form.get('species', '').strip()
        breed = request.form.get('breed', '').strip() or None
        age = request.form.get('age', '').strip()
        weight = request.form.get('weight', '').strip()

        if not name or not species:
            flash('Nombre y especie son obligatorios.', 'danger')
            return render_template('owner/add_pet.html')

        try:
            age = int(age) if age else None
            weight = float(weight) if weight else None
        except ValueError:
            flash('Edad y peso deben ser valores numéricos.', 'danger')
            return render_template('owner/add_pet.html')

        pet = Pet(
            name=name,
            species=species,
            breed=breed,
            age=age,
            weight=weight,
            owner_id=session['user_id'],
        )
        db.session.add(pet)
        db.session.commit()
        flash(f'Mascota "{name}" añadida correctamente.', 'success')
        return redirect(url_for('main.owner_dashboard'))

    return render_template('owner/add_pet.html')


@main.route('/owner/pets/<int:pet_id>')
@owner_required
def pet_detail(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.owner_id != session['user_id']:
        flash('No tienes permiso para ver esta mascota.', 'danger')
        return redirect(url_for('main.owner_dashboard'))
    return render_template('owner/pet_detail.html', pet=pet)


@main.route('/owner/pets/<int:pet_id>/consultation', methods=['GET', 'POST'])
@owner_required
def request_consultation(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.owner_id != session['user_id']:
        flash('No tienes permiso para gestionar esta mascota.', 'danger')
        return redirect(url_for('main.owner_dashboard'))

    if request.method == 'POST':
        date_str = request.form.get('date', '').strip()
        reason = request.form.get('reason', '').strip()

        if not date_str or not reason:
            flash('Fecha y motivo son obligatorios.', 'danger')
            return render_template('owner/request_consultation.html', pet=pet)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash('Formato de fecha inválido.', 'danger')
            return render_template('owner/request_consultation.html', pet=pet)

        consultation = Consultation(date=date, reason=reason, pet_id=pet.id)
        db.session.add(consultation)
        db.session.commit()
        flash('Consulta solicitada correctamente.', 'success')
        return redirect(url_for('main.pet_detail', pet_id=pet.id))

    return render_template('owner/request_consultation.html', pet=pet)


# ---------------------------------------------------------------------------
# Vet routes
# ---------------------------------------------------------------------------

@main.route('/vet/dashboard')
@vet_required
def vet_dashboard():
    pending = (
        Consultation.query
        .filter_by(status='pendiente')
        .order_by(Consultation.date)
        .all()
    )
    attended = (
        Consultation.query
        .filter_by(status='atendida')
        .order_by(Consultation.date.desc())
        .all()
    )
    return render_template('vet/dashboard.html', pending=pending, attended=attended)


@main.route('/vet/consultations/<int:consultation_id>')
@vet_required
def consultation_detail(consultation_id):
    consultation = Consultation.query.get_or_404(consultation_id)
    return render_template('vet/consultation_detail.html', consultation=consultation)


@main.route('/vet/consultations/<int:consultation_id>/record', methods=['GET', 'POST'])
@vet_required
def add_medical_record(consultation_id):
    consultation = Consultation.query.get_or_404(consultation_id)
    record = consultation.medical_record

    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis', '').strip() or None
        treatment = request.form.get('treatment', '').strip() or None
        observations = request.form.get('observations', '').strip() or None

        if record is None:
            record = MedicalRecord(consultation_id=consultation.id)
            db.session.add(record)

        record.diagnosis = diagnosis
        record.treatment = treatment
        record.observations = observations

        consultation.status = 'atendida'
        consultation.vet_id = session['user_id']

        db.session.commit()
        flash('Registro médico guardado correctamente.', 'success')
        return redirect(url_for('main.consultation_detail', consultation_id=consultation.id))

    return render_template('vet/add_medical_record.html', consultation=consultation, record=record)
