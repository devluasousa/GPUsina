from flask import Flask, render_template, request, redirect, url_for, abort
import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Lista de IPs permitidos
ALLOWED_IPS = ['192.168.2.137', '127.0.0.1', '152.249.143.223']

app = Flask(__name__)

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in ALLOWED_IPS:
        abort(403)  # Aborta a solicitação com status de proibido se não estiver no IP permitido
        
# Configure o Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'gestaopontousina-a32a6ea09560.json'

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)
# ID da sua planilha
SPREADSHEET_ID = '1144zWwPY4atubZ--ZtIabpMeqeIj_0uMOoVXCfPTyTQ'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Obter valores do formulário
        nome = request.form.get('nome')
        action = request.form.get('action')
        # Ler a data e hora atual
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Escrever no Google Sheets
        range_ = 'Registros!A2:C' 
        values = [
            [now, nome, action]
        ]
        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=range_,
            valueInputOption='USER_ENTERED', body=body).execute()

        return redirect(url_for('home'))
    else:
        # Obter nomes da planilha
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range='Cadastro!A2:A').execute()
        nomes = result.get('values', [])
        # Transforma em uma lista simples
        nomes = [nome[0] for nome in nomes if nome]
        return render_template('index.html', nomes=nomes, current_time=datetime.datetime.now())

if __name__ == '__main__':
    app.run(debug=True)
