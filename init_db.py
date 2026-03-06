from sqlalchemy import text

from app import create_app, db


app = create_app()


def ensure_image_columns() -> None:
    try:
        with db.engine.begin() as conn:
            imagen_exists = conn.execute(
                text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_name='mascotas' AND column_name='imagen'"
                )
            ).first()
            if imagen_exists is None:
                conn.execute(text("ALTER TABLE mascotas ADD COLUMN imagen bytea"))

            mimetype_exists = conn.execute(
                text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_name='mascotas' AND column_name='imagen_mimetype'"
                )
            ).first()
            if mimetype_exists is None:
                conn.execute(text("ALTER TABLE mascotas ADD COLUMN imagen_mimetype VARCHAR(150)"))
    except Exception as exc:
        print("Warning: could not ensure image columns exist:", exc)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        ensure_image_columns()
    print("Database initialization completed.")
