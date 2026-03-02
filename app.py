import os
from flask import Flask
from extensions import db, migrate
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from routes import main
    app.register_blueprint(main)

    with app.app_context():
        import models  # noqa: F401 – ensure models are registered before create_all
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug)
