from app import db
from datetime import datetime

class Chamado(db.Model):

    __tablename__ = 'chamados'

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(200), nullable=False)

    descricao = db.Column(db.Text)

    status = db.Column(
        db.String(50),
        default='Aberto'
    )

    prioridade = db.Column(
        db.String(50),
        default='Normal'
    )

    data_abertura = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    solicitante = db.Column(db.String(100))

    equipamento_id = db.Column(
        db.Integer,
        db.ForeignKey('equipamentos.id')
    )

    equipamento = db.relationship(
    'Equipamento',
    backref='chamados'
    )

    tecnico_responsavel = db.Column(
    db.String(100)
    )