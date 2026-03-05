from app import create_app, db
from sqlalchemy import text

app = create_app()

from app import routes


def ensure_image_columns():
    """Ensure `imagen` and `imagen_mimetype` columns exist on `mascotas` table.
    This is a development-time convenience (not a replacement for migrations).
    """
    try:
        with db.engine.begin() as conn:
            
            r = conn.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name='mascotas' AND column_name='imagen'"))
            if r.first() is None:
                conn.execute(text("ALTER TABLE mascotas ADD COLUMN imagen bytea"))

            r = conn.execute(text("SELECT 1 FROM information_schema.columns WHERE table_name='mascotas' AND column_name='imagen_mimetype'"))
            if r.first() is None:
                conn.execute(text("ALTER TABLE mascotas ADD COLUMN imagen_mimetype VARCHAR(150)"))
    except Exception as e:
        print('Warning: could not ensure image columns exist:', e)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        ensure_image_columns()
    app.run(debug=True)