from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'main.login'

    from app.routes.main_routes import main
    app.register_blueprint(main)

    @app.errorhandler(403)
    def acesso_negado(error):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def pagina_nao_encontrada(error):
        return render_template('404.html'), 404

    return app


from app.models.user import User
from app.models.equipamento import Equipamento
from app.models.manutencao import Manutencao
from app.models.chamado import Chamado
from app.models.comentario_chamado import ComentarioChamado
from app.models.anexo_chamado import AnexoChamado


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))