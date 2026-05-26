from app import db
from datetime import datetime

class Manutencao(db.Model):

    __tablename__ = 'manutencoes'

    id = db.Column(db.Integer, primary_key=True)

    equipamento_id = db.Column(
        db.Integer,
        db.ForeignKey('equipamentos.id')
    )

    tipo = db.Column(db.String(100))

    descricao = db.Column(db.Text)

    data_manutencao = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    proxima_manutencao = db.Column(db.Date)

    status = db.Column(db.String(50), default='Concluída')