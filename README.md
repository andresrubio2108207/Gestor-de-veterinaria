# Gestor de Veterinaria (PetCare)

Aplicacion web hecha con Flask para gestionar usuarios, mascotas, historial medico y consultas veterinarias.

## Tecnologias
- Python 3
- Flask + SQLAlchemy
- PostgreSQL
- Jinja2 + CSS/JS
- Pytest

## Ejecucion rapida
1. Crear y activar entorno virtual.
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configurar variables en `.env`:
   - `SECRET_KEY`
   - `DATABASE_URL`
4. Iniciar la app:
   ```bash
   python main.py
   ```

## Tests
```bash
pytest
```

## Estructura principal
- `app/models/`: modelos de base de datos
- `app/routes/`: rutas y vistas
- `app/templates/`: plantillas HTML
- `app/static/`: estilos y scripts
- `tests/`: pruebas automatizadas
