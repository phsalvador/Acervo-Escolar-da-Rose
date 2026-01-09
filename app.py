import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'escola_segura_2026'
# O arquivo 'escola.db' será criado na mesma pasta do projeto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///escola.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELOS DO BANCO DE DADOS ---

class Professor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Criar o banco e um professor inicial (Admin)
def setup_db():
    with app.app_context():
        db.create_all()
        if not Professor.query.filter_by(username='admin').first():
            hashed_pw = generate_password_hash('admin123', method='pbkdf2:sha256')
            admin = Professor(username='admin', password=hashed_pw)
            db.session.add(admin)
            db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return Professor.query.get(int(user_id))

SERIES = ['1_ano', '2_ano', '3_ano', '4_ano', '5_ano']

# --- ROTAS ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Professor.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        flash('Login inválido!')
    return render_template('login.html')

@app.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar():
    # Apenas o admin pode criar novos professores (opcional)
    if request.method == 'POST':
        novo_user = request.form.get('username')
        nova_senha = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')
        
        if Professor.query.filter_by(username=novo_user).first():
            flash('Usuário já existe!')
        else:
            p = Professor(username=novo_user, password=nova_senha)
            db.session.add(p)
            db.session.commit()
            flash('Professor cadastrado!')
    return render_template('registrar.html')

# (Mantenha as rotas de index, upload e download do passo anterior)

if __name__ == '__main__':
    setup_db() # Cria o banco de dados na primeira execução
    app.run(debug=True)

@app.route('/download/<serie>/<filename>')
@login_required
def baixar_arquivo(serie, filename):
    # Verifica se o arquivo existe antes de tentar baixar
    diretorio = os.path.join(app.config['UPLOAD_FOLDER'], serie)
    if os.path.exists(os.path.join(diretorio, filename)):
        return send_from_directory(diretorio, filename)
    else:
        return "Arquivo não encontrado", 404
