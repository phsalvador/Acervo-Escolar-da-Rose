import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma_chave_muito_segura_123' # Mude isso em produção
app.config['UPLOAD_FOLDER'] = 'uploads'

# Configuração do Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Mock de Banco de Dados de Professores (Substitua por um DB real futuramente)
users = {'professor_joao': {'password': 'senha123'}, 'admin': {'password': 'admin'}}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id not in users:
        return None
    return User(user_id)

SERIES = ['1_ano', '2_ano', '3_ano', '4_ano', '5_ano']

# Criar pastas iniciais
for serie in SERIES:
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], serie), exist_ok=True)

# --- ROTAS ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        flash('Usuário ou senha inválidos!')
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html', series=SERIES, user=current_user.id)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files.get('file')
    serie = request.form.get('serie')
    
    if file and serie in SERIES:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], serie, filename)
        file.save(save_path)
        return f"Professor {current_user.id}, arquivo salvo com sucesso em {serie}!"
    
    return "Erro no upload."

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

from flask import send_from_directory

# ... (mantenha o código anterior)

@app.route('/arquivos/<serie>')
@login_required
def listar_arquivos(serie):
    if serie not in SERIES:
        return "Série inválida", 404
    
    caminho_serie = os.path.join(app.config['UPLOAD_FOLDER'], serie)
    arquivos = os.listdir(caminho_serie)
    return render_template('arquivos.html', serie=serie, arquivos=arquivos)

@app.route('/download/<serie>/<filename>')
@login_required
def baixar_arquivo(serie, filename):
    diretorio = os.path.join(app.config['UPLOAD_FOLDER'], serie)
    return send_from_directory(diretorio, filename)
