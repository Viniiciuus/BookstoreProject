from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Usuario, Livro  # Importando modelos do models.py
from seed import inicializar_catalogo
from carrinho import carrinho_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-super-secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Inicializa a extensão SQLAlchemy com a app

login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.register_blueprint(carrinho_bp)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@app.route('/')
def index():
    livros = Livro.query.all()
    interesses = session.get('interesses', [])
    livros_interesse = [Livro.query.get(id) for id in interesses[-3:] if Livro.query.get(id)]  # Últimos 3
    return render_template('index.html', user=current_user, livros=livros, livros_interesse=livros_interesse)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
            return redirect(url_for('register'))

        usuario = Usuario(nome=nome, email=email, senha=generate_password_hash(senha))
        db.session.add(usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos.', 'error')

    return render_template('login.html')


# ... (imports existentes, incluindo from flask import Flask, render_template, request, etc.)

@app.route('/busca', methods=['GET', 'POST'])
def busca():
    if request.method == 'POST':
        termo = request.form.get('termo', '').lower()
        if termo:
            return redirect(url_for('resultados', termo=termo))
    return redirect(url_for('index'))

@app.route('/resultados')
def resultados():
    termo = request.args.get('termo', '').lower()
    livros = Livro.query.all()  # Padrão: todos os livros
    if termo:
        livros = Livro.query.filter(
            db.or_(
                Livro.titulo.ilike(f'%{termo}%'),
                Livro.autor.ilike(f'%{termo}%')
            )
        ).all()
    return render_template('resultados.html', livros=livros, termo=termo)


@app.route('/livro/<int:id>')
def detalhes_livro(id):
    livro = Livro.query.get_or_404(id)
    if 'interesses' not in session:
        session['interesses'] = []
    # Atualiza interesses e limita a 3
    if id not in session['interesses']:
        session['interesses'].append(id)
    if len(session['interesses']) > 3:
        session['interesses'] = session['interesses'][-3:]
    # Força a sessão a ser salva
    session.modified = True
    return render_template('detalhes_livro.html', livro=livro)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    livros = Livro.query.all()
    interesses = session.get('interesses', [])
    livros_interesse = [Livro.query.get(id) for id in interesses[-3:] if Livro.query.get(id)]  # Últimos 3
    return render_template('dashboard.html', user=current_user, livros=livros, livros_interesse=livros_interesse)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas para Usuario e Livro
        inicializar_catalogo()
    app.run(debug=True)