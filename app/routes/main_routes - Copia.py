from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import date
import os
import uuid

from app import db
from app.models.equipamento import Equipamento
from app.models.user import User
from app.models.manutencao import Manutencao
from app.models.chamado import Chamado
from app.models.comentario_chamado import ComentarioChamado
from app.models.anexo_chamado import AnexoChamado


main = Blueprint('main', __name__)


def is_admin():
    return current_user.tipo == 'admin'


def pode_gerenciar_equipamentos():
    return current_user.tipo in ['admin', 'tecnico']


def pode_acessar_chamado(chamado):
    if current_user.tipo in ['admin', 'tecnico']:
        return True

    return chamado.solicitante == current_user.username


def salvar_arquivo_upload(arquivo, pasta):

    if not arquivo or arquivo.filename == '':
        return None

    extensoes_permitidas = {
        'png',
        'jpg',
        'jpeg',
        'gif',
        'pdf'
    }

    if '.' not in arquivo.filename:

        flash('Arquivo inválido!', 'danger')

        return None

    extensao = arquivo.filename.rsplit('.', 1)[-1].lower()

    if extensao not in extensoes_permitidas:

        flash('Tipo de arquivo não permitido!', 'danger')

        return None

    nome_arquivo = f'{uuid.uuid4()}.{extensao}'

    caminho = os.path.join(pasta, nome_arquivo)

    arquivo.save(caminho)

    return nome_arquivo


@main.route('/')
@login_required
def home():

    if current_user.tipo == 'usuario':

        meus_chamados = Chamado.query.filter_by(
            solicitante=current_user.username
        )

        chamados_abertos = meus_chamados.filter_by(status='Aberto').count()
        chamados_andamento = meus_chamados.filter_by(status='Em andamento').count()
        chamados_finalizados = meus_chamados.filter_by(status='Finalizado').count()

        ultimos_chamados = meus_chamados.order_by(
            Chamado.id.desc()
        ).limit(5)

        return render_template(
            'home.html',
            modo_usuario=True,
            chamados_abertos=chamados_abertos,
            chamados_andamento=chamados_andamento,
            chamados_finalizados=chamados_finalizados,
            ultimos_chamados=ultimos_chamados
        )

    ultimos_chamados = Chamado.query.order_by(
        Chamado.id.desc()
    ).limit(5)

    chamados_abertos = Chamado.query.filter_by(status='Aberto').count()
    chamados_andamento = Chamado.query.filter_by(status='Em andamento').count()
    chamados_finalizados = Chamado.query.filter_by(status='Finalizado').count()

    manutencoes_pendentes = Manutencao.query.filter(
        Manutencao.proxima_manutencao <= date.today()
    ).all()

    total_equipamentos = Equipamento.query.count()

    equipamentos_ativos = Equipamento.query.filter_by(
        status='Ativo'
    ).count()

    ultimos_equipamentos = Equipamento.query.order_by(
        Equipamento.id.desc()
    ).limit(5)

    return render_template(
        'home.html',
        modo_usuario=False,
        total_equipamentos=total_equipamentos,
        equipamentos_ativos=equipamentos_ativos,
        ultimos_equipamentos=ultimos_equipamentos,
        manutencoes_pendentes=manutencoes_pendentes,
        chamados_abertos=chamados_abertos,
        chamados_andamento=chamados_andamento,
        chamados_finalizados=chamados_finalizados,
        ultimos_chamados=ultimos_chamados
    )


@main.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.ativo and check_password_hash(user.password, password):

            login_user(user)

            return redirect('/')

        flash('Usuário ou senha inválidos!', 'danger')

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect('/login')


@main.route('/equipamentos')
@login_required
def equipamentos():

    if not pode_gerenciar_equipamentos():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    busca = request.args.get('busca')
    status = request.args.get('status')

    query = Equipamento.query

    if busca:

        query = query.filter(
            (Equipamento.nome.contains(busca)) |
            (Equipamento.patrimonio.contains(busca)) |
            (Equipamento.ip.contains(busca)) |
            (Equipamento.usuario_responsavel.contains(busca)) |
            (Equipamento.setor.contains(busca)) |
            (Equipamento.marca.contains(busca)) |
            (Equipamento.modelo.contains(busca))
        )

    if status:

        query = query.filter(
            Equipamento.status == status
        )

    page = request.args.get('page', 1, type=int)

    equipamentos = query.paginate(
        page=page,
        per_page=10
    )

    return render_template(
        'equipamentos.html',
        equipamentos=equipamentos
    )


@main.route('/equipamentos/novo', methods=['GET', 'POST'])
@login_required
def novo_equipamento():

    if not pode_gerenciar_equipamentos():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    if request.method == 'POST':

        equipamento_existente = Equipamento.query.filter_by(
            patrimonio=request.form['patrimonio']
        ).first()

        if equipamento_existente:

            flash('Patrimônio já cadastrado!', 'danger')

            return redirect('/equipamentos/novo')

        nome_imagem = salvar_arquivo_upload(
            request.files.get('imagem'),
            'app/static/uploads'
        )

        equipamento = Equipamento(
            patrimonio=request.form['patrimonio'],
            nome=request.form['nome'],
            tipo=request.form['tipo'],
            marca=request.form['marca'],
            modelo=request.form['modelo'],
            numero_serie=request.form['numero_serie'],
            ip=request.form['ip'],
            usuario_responsavel=request.form['usuario_responsavel'],
            setor=request.form['setor'],
            observacoes=request.form['observacoes'],
            status=request.form['status'],
            imagem=nome_imagem
        )

        db.session.add(equipamento)
        db.session.commit()

        flash('Equipamento cadastrado com sucesso!', 'success')

        return redirect(url_for('main.home'))

    return render_template('novo_equipamento.html')


@main.route('/equipamentos/<int:id>')
@login_required
def visualizar_equipamento(id):

    if not pode_gerenciar_equipamentos():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    equipamento = Equipamento.query.get_or_404(id)

    return render_template(
        'visualizar_equipamento.html',
        equipamento=equipamento
    )


@main.route('/equipamentos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_equipamento(id):

    if not pode_gerenciar_equipamentos():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    equipamento = Equipamento.query.get_or_404(id)

    if request.method == 'POST':

        equipamento.nome = request.form['nome']
        equipamento.tipo = request.form['tipo']
        equipamento.marca = request.form['marca']
        equipamento.modelo = request.form['modelo']
        equipamento.numero_serie = request.form['numero_serie']
        equipamento.ip = request.form['ip']
        equipamento.usuario_responsavel = request.form['usuario_responsavel']
        equipamento.setor = request.form['setor']
        equipamento.status = request.form['status']
        equipamento.observacoes = request.form['observacoes']

        nova_imagem = request.files.get('imagem')

        if nova_imagem and nova_imagem.filename != '':

            nova_imagem = request.files.get('imagem')

            if nova_imagem and nova_imagem.filename != '':

                nome_nova_imagem = salvar_arquivo_upload(
                    nova_imagem,
                    'app/static/uploads'
                )

                if nome_nova_imagem:

                    if equipamento.imagem:

                        caminho_antigo = os.path.join(
                            'app/static/uploads',
                            equipamento.imagem
                        )

                        if os.path.exists(caminho_antigo):

                            os.remove(caminho_antigo)

                    equipamento.imagem = nome_nova_imagem

            equipamento.imagem = salvar_arquivo_upload(
                nova_imagem,
                'app/static/uploads'
            )

        db.session.commit()

        flash('Equipamento atualizado com sucesso!', 'success')

        return redirect('/equipamentos')

    return render_template(
        'editar_equipamento.html',
        equipamento=equipamento
    )


@main.route('/equipamentos/<int:id>/excluir')
@login_required
def excluir_equipamento(id):

    if not pode_gerenciar_equipamentos():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    equipamento = Equipamento.query.get_or_404(id)

    if equipamento.imagem:

        caminho_imagem = os.path.join(
            'app/static/uploads',
            equipamento.imagem
        )

        if os.path.exists(caminho_imagem):

            os.remove(caminho_imagem)

    db.session.delete(equipamento)
    db.session.commit()

    flash('Equipamento excluído com sucesso!', 'success')

    return redirect('/equipamentos')


@main.route('/equipamentos/<int:id>/manutencao/nova', methods=['GET', 'POST'])
@login_required
def nova_manutencao(id):

    if not pode_gerenciar_equipamentos():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    equipamento = Equipamento.query.get_or_404(id)

    if request.method == 'POST':

        manutencao = Manutencao(
            equipamento_id=equipamento.id,
            tipo=request.form['tipo'],
            descricao=request.form['descricao'],
            proxima_manutencao=request.form['proxima_manutencao'],
            status=request.form['status']
        )

        db.session.add(manutencao)
        db.session.commit()

        flash('Manutenção registrada com sucesso!', 'success')

        return redirect(f'/equipamentos/{equipamento.id}')

    return render_template(
        'nova_manutencao.html',
        equipamento=equipamento
    )


@main.route('/manutencao/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_manutencao(id):

    if not pode_gerenciar_equipamentos():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    manutencao = Manutencao.query.get_or_404(id)

    if request.method == 'POST':

        manutencao.tipo = request.form['tipo']
        manutencao.descricao = request.form['descricao']
        manutencao.status = request.form['status']
        manutencao.proxima_manutencao = request.form['proxima_manutencao']

        db.session.commit()

        flash('Manutenção atualizada com sucesso!', 'success')

        return redirect(f'/equipamentos/{manutencao.equipamento_id}')

    return render_template(
        'editar_manutencao.html',
        manutencao=manutencao
    )


@main.route('/manutencao/<int:id>/excluir')
@login_required
def excluir_manutencao(id):

    if not pode_gerenciar_equipamentos():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    manutencao = Manutencao.query.get_or_404(id)

    equipamento_id = manutencao.equipamento_id

    db.session.delete(manutencao)
    db.session.commit()

    flash('Manutenção excluída com sucesso!', 'success')

    return redirect(f'/equipamentos/{equipamento_id}')


@main.route('/chamados')
@login_required
def chamados():

    busca = request.args.get('busca')
    status = request.args.get('status')
    tecnico = request.args.get('tecnico')

    if current_user.tipo == 'usuario':

        query = Chamado.query.filter_by(
            solicitante=current_user.username
        )

    else:

        query = Chamado.query

    if busca:

        query = query.filter(
            (Chamado.titulo.contains(busca)) |
            (Chamado.solicitante.contains(busca))
        )

    if status:

        query = query.filter(
            Chamado.status == status
        )

    if tecnico:

        query = query.filter(
            Chamado.tecnico_responsavel.contains(tecnico)
        )

    chamados = query.order_by(
        Chamado.id.desc()
    ).all()

    return render_template(
        'chamados.html',
        chamados=chamados
    )


@main.route('/chamados/novo', methods=['GET', 'POST'])
@login_required
def novo_chamado():

    equipamentos = Equipamento.query.all()

    if request.method == 'POST':

        chamado = Chamado(
            titulo=request.form['titulo'],
            descricao=request.form['descricao'],
            prioridade=request.form['prioridade'],
            status=request.form['status'],
            solicitante=current_user.username,
            tecnico_responsavel=None,
            equipamento_id=request.form['equipamento_id'],
        )

        db.session.add(chamado)
        db.session.commit()

        flash('Chamado aberto com sucesso!', 'success')

        return redirect('/')

    return render_template(
        'novo_chamado.html',
        equipamentos=equipamentos
    )


@main.route('/chamados/<int:id>')
@login_required
def visualizar_chamado(id):

    chamado = Chamado.query.get_or_404(id)

    if not pode_acessar_chamado(chamado):

        flash('Acesso negado!', 'danger')

        return redirect('/chamados')

    return render_template(
        'visualizar_chamado.html',
        chamado=chamado
    )


@main.route('/chamados/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_chamado(id):

    chamado = Chamado.query.get_or_404(id)

    if not pode_acessar_chamado(chamado):

        flash('Acesso negado!', 'danger')

        return redirect('/chamados')

    equipamentos = Equipamento.query.all()

    if request.method == 'POST':

        chamado.titulo = request.form['titulo']
        chamado.descricao = request.form['descricao']
        chamado.prioridade = request.form['prioridade']
        chamado.status = request.form['status']

        if current_user.tipo in ['admin', 'tecnico']:

            chamado.tecnico_responsavel = request.form['tecnico_responsavel']
            chamado.equipamento_id = request.form['equipamento_id']

        db.session.commit()

        flash('Chamado atualizado com sucesso!', 'success')

        return redirect('/chamados')

    return render_template(
        'editar_chamado.html',
        chamado=chamado,
        equipamentos=equipamentos
    )


@main.route('/chamados/<int:id>/excluir')
@login_required
def excluir_chamado(id):

    chamado = Chamado.query.get_or_404(id)

    if not pode_acessar_chamado(chamado):

        flash('Acesso negado!', 'danger')

        return redirect('/chamados')

    db.session.delete(chamado)
    db.session.commit()

    flash('Chamado excluído com sucesso!', 'success')

    return redirect('/chamados')

@main.route('/chamados/<int:id>/assumir')
@login_required
def assumir_chamado(id):

    if current_user.tipo not in ['admin', 'tecnico']:

        flash('Acesso negado!', 'danger')

        return redirect('/')

    chamado = Chamado.query.get_or_404(id)

    chamado.tecnico_responsavel = current_user.username
    chamado.status = 'Em andamento'

    comentario = ComentarioChamado(
        comentario=f'{current_user.username} assumiu o chamado.',
        chamado_id=chamado.id
    )

    db.session.add(comentario)

    db.session.commit()

    flash('Chamado assumido com sucesso!', 'success')

    return redirect(f'/chamados/{id}')


@main.route('/chamados/<int:id>/comentario', methods=['POST'])
@login_required
def adicionar_comentario(id):

    chamado = Chamado.query.get_or_404(id)

    if not pode_acessar_chamado(chamado):

        flash('Acesso negado!', 'danger')

        return redirect('/chamados')

    comentario = ComentarioChamado(
        comentario=request.form['comentario'],
        chamado_id=chamado.id
    )

    db.session.add(comentario)
    db.session.commit()

    flash('Comentário adicionado!', 'success')

    return redirect(f'/chamados/{chamado.id}')


@main.route('/chamados/<int:id>/anexo', methods=['POST'])
@login_required
def adicionar_anexo(id):

    chamado = Chamado.query.get_or_404(id)

    if not pode_acessar_chamado(chamado):

        flash('Acesso negado!', 'danger')

        return redirect('/chamados')

    nome_arquivo = salvar_arquivo_upload(
        request.files.get('arquivo'),
        'app/static/uploads/chamados'
    )

    if nome_arquivo:

        anexo = AnexoChamado(
            arquivo=nome_arquivo,
            chamado_id=chamado.id
        )

        db.session.add(anexo)
        db.session.commit()

        flash('Anexo enviado com sucesso!', 'success')

    return redirect(f'/chamados/{chamado.id}')


@main.route('/usuarios')
@login_required
def usuarios():

    if not is_admin():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    usuarios = User.query.order_by(
        User.id.desc()
    ).all()

    return render_template(
        'usuarios.html',
        usuarios=usuarios
    )


@main.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
def novo_usuario():

    if not is_admin():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        usuario_existente = User.query.filter_by(
            username=username
        ).first()

        if usuario_existente:

            flash('Usuário já cadastrado!', 'danger')

            return redirect('/usuarios/novo')

        usuario = User(
            username=username,
            password=generate_password_hash(password),
            tipo=request.form['tipo']
        )

        db.session.add(usuario)
        db.session.commit()

        flash('Usuário cadastrado com sucesso!', 'success')

        return redirect('/usuarios')

    return render_template('novo_usuario.html')


@main.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):

    if not is_admin():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    usuario = User.query.get_or_404(id)

    if request.method == 'POST':

        usuario.username = request.form['username']
        usuario.tipo = request.form['tipo']

        nova_senha = request.form['password']

        if nova_senha:

            usuario.password = generate_password_hash(nova_senha)

        db.session.commit()

        flash('Usuário atualizado com sucesso!', 'success')

        return redirect('/usuarios')

    return render_template(
        'editar_usuario.html',
        usuario=usuario
    )


@main.route('/usuarios/<int:id>/desativar')
@login_required
def desativar_usuario(id):

    if not is_admin():

        flash('Acesso negado!', 'danger')

        return redirect('/')

    usuario = User.query.get_or_404(id)

    if usuario.id == current_user.id:

        flash('Você não pode desativar seu próprio usuário.', 'danger')

        return redirect('/usuarios')

    usuario.ativo = False

    db.session.commit()

    flash('Usuário desativado com sucesso!', 'success')

    return redirect('/usuarios')