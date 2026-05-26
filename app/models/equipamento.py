from app import db

class Equipamento(db.Model):

    __tablename__ = 'equipamentos'

    id = db.Column(db.Integer, primary_key=True)

    patrimonio = db.Column(db.String(50), unique=True, nullable=False)

    nome = db.Column(db.String(100), nullable=False)

    tipo = db.Column(db.String(50))

    marca = db.Column(db.String(100))

    modelo = db.Column(db.String(100))

    numero_serie = db.Column(db.String(100))

    ip = db.Column(db.String(50))

    usuario_responsavel = db.Column(db.String(100))

    setor = db.Column(db.String(100))

    status = db.Column(db.String(50), default='Ativo')

    observacoes = db.Column(db.Text)

    manutencoes = db.relationship(
    'Manutencao',
    backref='equipamento',
    lazy=True
    )

    imagem = db.Column(db.String(255))