import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
SERIES = ['1_ano', '2_ano', '3_ano', '4_ano', '5_ano']

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Criar pastas se não existirem
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
for serie in SERIES:
    path = os.path.join(UPLOAD_FOLDER, serie)
    if not os.path.exists(path):
        os.makedirs(path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', series=SERIES)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado"
    
    file = request.files['file']
    serie_selecionada = request.form.get('serie')
    
    if file and allowed_file(file.filename) and serie_selecionada in SERIES:
        filename = secure_filename(file.filename)
        # Salva o arquivo na pasta da série correspondente
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], serie_selecionada, filename)
        file.save(save_path)
        return f"Arquivo '{filename}' armazenado com sucesso em {serie_selecionada}!"
    
    return "Falha no upload. Verifique o formato do arquivo."

if __name__ == '__main__':
    app.run(debug=True)
