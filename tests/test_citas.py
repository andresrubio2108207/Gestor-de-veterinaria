from datetime import datetime, timedelta

from app import db
from app.models.consulta import Consulta
from app.models.mascota import Mascota
from app.models.usuario import User
from app.models.veterinario import Veterinario
from app.services.auth_service import registrar_usuario


def _set_session(client, user):
    with client.session_transaction() as sess:
        sess["user_id"] = user.id
        sess["nombre"] = user.nombre
        sess["tipo"] = user.tipo


def test_registro_por_tipo_crea_subclases(app):
    with app.app_context():
        ok_dueno, _ = registrar_usuario("Dueno Test", "dueno@test.com", "123456", "dueno")
        ok_vet, _ = registrar_usuario("Vet Test", "vet@test.com", "123456", "veterinario")

        assert ok_dueno is True
        assert ok_vet is True
        assert User.query.filter_by(correo="dueno@test.com").first() is not None
        assert Veterinario.query.filter_by(correo="vet@test.com").first() is not None


def test_agendar_cita_crea_registro_futuro(app, client):
    with app.app_context():
        registrar_usuario("Dueno Test", "dueno2@test.com", "123456", "dueno")
        registrar_usuario("Vet Test", "vet2@test.com", "123456", "veterinario")

        dueno = User.query.filter_by(correo="dueno2@test.com").first()
        mascota = Mascota(nombre="Luna", especie="Perro", raza="Mestizo", edad=3, dueno_id=dueno.id)
        db.session.add(mascota)
        db.session.commit()
        mascota_id = mascota.id

        _set_session(client, dueno)
        fecha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    response = client.post(
        "/consultas",
        data={
            "mascota_id": str(mascota_id),
            "tipo": "salud",
            "fecha_cita": fecha,
            "hora_cita": "10:30",
            "modalidad": "presencial",
            "mensaje": "Control anual",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    with app.app_context():
        cita = Consulta.query.filter_by(mascota_id=mascota_id).first()
        assert cita is not None
        assert cita.estado == "agendada"


def test_cancelar_cita_cambia_estado(app, client):
    with app.app_context():
        registrar_usuario("Dueno Test", "dueno3@test.com", "123456", "dueno")
        registrar_usuario("Vet Test", "vet3@test.com", "123456", "veterinario")

        dueno = User.query.filter_by(correo="dueno3@test.com").first()
        vet = Veterinario.query.filter_by(correo="vet3@test.com").first()

        mascota = Mascota(nombre="Milo", especie="Gato", raza="Criollo", edad=2, dueno_id=dueno.id)
        db.session.add(mascota)
        db.session.commit()

        cita = Consulta(
            fecha=datetime.now() + timedelta(days=2),
            motivo="Vacuna",
            mascota_id=mascota.id,
            veterinario_id=vet.id,
            estado="agendada",
        )
        db.session.add(cita)
        db.session.commit()

        _set_session(client, dueno)
        cita_id = cita.id

    response = client.post(f"/consultas/{cita_id}/cancelar", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        cita_actualizada = db.session.get(Consulta, cita_id)
        assert cita_actualizada.estado == "cancelada"


def test_consultas_muestra_solo_futuras_en_agendadas(app, client):
    with app.app_context():
        registrar_usuario("Dueno Test", "dueno4@test.com", "123456", "dueno")
        registrar_usuario("Vet Test", "vet4@test.com", "123456", "veterinario")

        dueno = User.query.filter_by(correo="dueno4@test.com").first()
        vet = Veterinario.query.filter_by(correo="vet4@test.com").first()

        mascota = Mascota(nombre="Nina", especie="Perro", raza="Pug", edad=4, dueno_id=dueno.id)
        db.session.add(mascota)
        db.session.commit()

        cita_pasada = Consulta(
            fecha=datetime.now() - timedelta(days=1),
            motivo="MOTIVO_PASADO_TEST",
            mascota_id=mascota.id,
            veterinario_id=vet.id,
            estado="agendada",
        )
        cita_futura = Consulta(
            fecha=datetime.now() + timedelta(days=3),
            motivo="MOTIVO_FUTURO_TEST",
            mascota_id=mascota.id,
            veterinario_id=vet.id,
            estado="agendada",
        )
        db.session.add(cita_pasada)
        db.session.add(cita_futura)
        db.session.commit()

        _set_session(client, dueno)

    response = client.get("/consultas")
    html = response.get_data(as_text=True)
    agendadas_html = html.split("Mis citas agendadas", 1)[1].split("Citas pasadas y canceladas", 1)[0]

    assert response.status_code == 200
    assert "MOTIVO_FUTURO_TEST" in agendadas_html
    assert "MOTIVO_PASADO_TEST" not in agendadas_html
    assert "MOTIVO_PASADO_TEST" in html
    assert "Citas pasadas y canceladas" in html
