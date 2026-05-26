from app import db
from datetime import datetime

class AnexoChamado(db.Model):

    __tablename__ = 'anexos_chamado'

    id = db.Column(db.Integer, primary_key=True)

    arquivo = db.Column(db.String(255), nullable=False)

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
        backref='anexos'
    )