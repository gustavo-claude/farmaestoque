from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

app = Flask(__name__)
app.secret_key = 'bNCM$S@QurG%ajKUt%RmbknX7h'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/controle_estoque_farmacia'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class Medicamento(db.Model):
    __tablename__ = 'medicamentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    principio_ativo = db.Column(db.String(255), nullable=False)
    laboratorio = db.Column(db.String(255), nullable=False)
    codigo_barras = db.Column(db.String(255), unique=True)
    preco_custo = db.Column(db.Numeric(10, 2))
    preco_venda = db.Column(db.Numeric(10, 2))
    data_cadastro = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False) # Adicionando a chave estrangeira para o usuário
    entradas = db.relationship('Entrada', backref='medicamento', lazy=True)
    saidas = db.relationship('Saida', backref='medicamento', lazy=True)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False) # Alteramos 'senha' para 'senha_hash'
    nivel_acesso = db.Column(db.String(50), nullable=False)
    entradas = db.relationship('Entrada', backref='usuario', lazy=True)
    saidas = db.relationship('Saida', backref='usuario', lazy=True)
    receitas = db.relationship('Receita', backref='usuario', lazy=True)

    @property
    def senha(self):
        raise AttributeError('senha não é um atributo legível')

    @senha.setter
    def senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
        
class Receita(db.Model):
    __tablename__ = 'receitas'
    id = db.Column(db.Integer, primary_key=True)
    codigo_receita = db.Column(db.String(255), unique=True, nullable=False)
    data_emissao = db.Column(db.Date, nullable=False)
    paciente_nome = db.Column(db.String(255))
    medico_nome = db.Column(db.String(255))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    saidas = db.relationship('Saida', backref='receita', lazy=True)

class Entrada(db.Model):
    __tablename__ = 'entradas'
    id = db.Column(db.Integer, primary_key=True)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamentos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_entrada = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    lote = db.Column(db.String(255))
    data_validade = db.Column(db.Date)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

class Saida(db.Model):
    __tablename__ = 'saidas'
    id = db.Column(db.Integer, primary_key=True)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamentos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_saida = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    tipo_saida = db.Column(db.String(50), nullable=False)
    receita_id = db.Column(db.Integer, db.ForeignKey('receitas.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)


@app.route('/')
def index():
    if 'usuario_id' in session:
        usuario = Usuario.query.get(session['usuario_id'])
        return render_template('index.html', usuario=usuario)
    else:
        return redirect(url_for('login')) # Se não estiver logado, redireciona para a tela de login
    
@app.route('/nova_entrada')
def exibir_formulario_entrada():
    medicamentos = Medicamento.query.all()
    return render_template('entrada_medicamento.html', medicamentos=medicamentos)

@app.route('/registrar_entrada', methods=['POST'])
def registrar_entrada():
    if request.method == 'POST':
        medicamento_id = int(request.form['medicamento_id'])
        lote = request.form.get('lote')
        data_validade = request.form.get('data_validade')
        quantidade = int(request.form['quantidade'])
        usuario_id = session.get('usuario_id')

        if usuario_id:
            nova_entrada = Entrada(
                medicamento_id=medicamento_id,
                quantidade=quantidade,
                lote=lote,
                data_validade=data_validade,
                usuario_id=usuario_id
            )
            db.session.add(nova_entrada)
            db.session.commit()
            return "Entrada de medicamento registrada com sucesso!"
        else:
            return redirect(url_for('login'))

    return redirect(url_for('exibir_formulario_entrada'))

@app.route('/novo_usuario')
def exibir_formulario_novo_usuario():
    return render_template('novo_usuario.html')

@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        email = request.form['email']
        senha = request.form['senha']
        nivel_acesso = request.form['nivel_acesso']

        novo_usuario = Usuario(nome=nome, cpf=cpf, email=email, nivel_acesso=nivel_acesso)
        novo_usuario.senha = senha # A senha será hasheada ao atribuir
        db.session.add(novo_usuario)
        db.session.commit()

        return "Usuário registrado com sucesso!"

    return redirect(url_for('exibir_formulario_novo_usuario'))

@app.route('/nova_receita')
def exibir_formulario_nova_receita():
    return render_template('nova_receita.html')

@app.route('/registrar_receita', methods=['POST'])
def registrar_receita():
    if request.method == 'POST':
        codigo_receita = request.form['codigo_receita']
        data_emissao = request.form['data_emissao']
        paciente_nome = request.form.get('paciente_nome')
        medico_nome = request.form.get('medico_nome')
        usuario_id = request.form['usuario_id'] # Recebendo o ID do usuário (por enquanto fixo)

        nova_receita = Receita(
            codigo_receita=codigo_receita,
            data_emissao=data_emissao,
            paciente_nome=paciente_nome,
            medico_nome=medico_nome,
            usuario_id=usuario_id
        )
        db.session.add(nova_receita)
        db.session.commit()

        return "Receita registrada com sucesso!" # Mensagem temporária

    return redirect(url_for('exibir_formulario_nova_receita'))

@app.route('/saida_direta')
def exibir_formulario_saida_direta():
    return render_template('saida_medicamento_direta.html')

@app.route('/registrar_saida_direta', methods=['POST'])
def registrar_saida_direta():
    if request.method == 'POST':
        medicamento_id = int(request.form['medicamento_id'])
        quantidade = int(request.form['quantidade'])
        tipo_saida = request.form['tipo_saida']
        usuario_id = request.form['usuario_id']

        nova_saida = Saida(
            medicamento_id=medicamento_id,
            quantidade=quantidade,
            tipo_saida=tipo_saida,
            usuario_id=usuario_id,
            receita_id=None # Indica que não está associada a uma receita
        )
        db.session.add(nova_saida)
        db.session.commit()

        return "Saída de medicamento registrada com sucesso!" # Mensagem temporária

    return redirect(url_for('exibir_formulario_saida_direta'))
    
@app.route('/login')
def exibir_formulario_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    cpf = request.form['cpf']
    senha = request.form['senha']
    usuario = Usuario.query.filter_by(cpf=cpf).first()

    if usuario and usuario.verificar_senha(senha):
        session['usuario_id'] = usuario.id
        # Obter o primeiro nome
        primeiro_nome = usuario.nome.split()[0]
        session['nome_usuario'] = primeiro_nome
        session['nivel_acesso'] = usuario.nivel_acesso
        return redirect(url_for('index')) # Redirecionar para a página inicial após o login
    else:
        return "CPF ou senha incorretos!" # Mensagem de erro temporária

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('login'))
    
@app.route('/cadastro_medicamento')
def exibir_formulario_cadastro_medicamento():
    return render_template('cadastro_medicamento.html')

@app.route('/registrar_medicamento', methods=['POST'])
def registrar_medicamento():
    if request.method == 'POST':
        nome = request.form['nome']
        principio_ativo = request.form['principio_ativo']
        laboratorio = request.form['laboratorio']
        codigo_barras = request.form.get('codigo_barras')
        preco_custo = request.form.get('preco_custo')
        usuario_id = session.get('usuario_id') # Obtém o ID do usuário logado

        if usuario_id:
            novo_medicamento = Medicamento(
                nome=nome,
                principio_ativo=principio_ativo,
                laboratorio=laboratorio,
                codigo_barras=codigo_barras,
                preco_custo=preco_custo,
                usuario_id=usuario_id # Salva o ID do usuário que cadastrou
            )
            db.session.add(novo_medicamento)
            db.session.commit()
            return "Medicamento cadastrado com sucesso!" # Mensagem temporária
        else:
            return redirect(url_for('login')) # Se não estiver logado, redireciona para o login

    return redirect(url_for('cadastro_medicamento'))

if __name__ == '__main__':
    #with app.app_context():
        # db.create_all() # Comente ou remova esta linha se as tabelas já existem
    app.run(debug=True)