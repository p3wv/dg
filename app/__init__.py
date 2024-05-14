from flask import Flask, send_from_directory
from flask_bootstrap import Bootstrap4
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from app.config import config
from flask_login import LoginManager
import os
from .commands import deploy_cli

bootstrap = Bootstrap4()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = 'auth.login' # type: ignore

def create_app():
    app = Flask(__name__)

    config_name = os.getenv('FLASKCONFIG') or 'default'
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    Session(app)
    
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    app.cli.add_command(deploy_cli)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
