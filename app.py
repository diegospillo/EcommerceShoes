from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from routes import bp as main_bp


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/ecommerceshoes'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(main_bp)
    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
