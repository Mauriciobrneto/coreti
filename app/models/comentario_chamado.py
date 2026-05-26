from app import db
from datetime import datetime

class ComentarioChamado(db.Model):

    __tablename__ = 'comentarios_chamado'

    id = db.Column(db.Integer, primary_key=True)

    comentario = db.Column(
        db.Text,
        nullable=False
    )

    data = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    chamado_id = db.Column(
        db.Integer,
        db.ForeignKey('chamados.id')
    )

    chamado = db.relationship(
        'Chamado',
        backref='comentarios'
    )