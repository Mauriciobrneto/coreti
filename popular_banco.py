from app import create_app, db
from app.models.equipamento import Equipamento
from app.models.manutencao import Manutencao
from datetime import date, timedelta
import random

app = create_app()

with app.app_context():

    for i in range(1, 21):

        equipamento = Equipamento(

            patrimonio=f'PC-{1000 + i}',

            nome=f'Computador {i}',

            tipo='Computador',

            marca=random.choice([
                'Dell',
                'HP',
                'Lenovo'
            ]),

            modelo='Desktop',

            numero_serie=f'SN{i}',

            ip=f'192.168.0.{i}',

            usuario_responsavel=f'Usuário {i}',

            setor=random.choice([
                'RH',
                'Financeiro',
                'Informática',
                'Compras'
            ]),

            status=random.choice([
                'Ativo',
                'Manutenção',
                'Baixado'
            ]),

            observacoes='Equipamento de teste'

        )

        db.session.add(equipamento)

        db.session.commit()

        manutencao = Manutencao(

            equipamento_id=equipamento.id,

            tipo='Limpeza Preventiva',

            descricao='Limpeza interna realizada',

            status=random.choice([
                'Concluída',
                'Pendente',
                'Em andamento'
            ]),

            proxima_manutencao=date.today() + timedelta(days=random.randint(-30, 30))

        )

        db.session.add(manutencao)

    db.session.commit()

    print('Banco populado com sucesso!')