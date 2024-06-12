from flask import Flask, render_template, request, redirect, url_for, abort
import datetime
import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Obtém os IPs permitidos das variáveis de ambiente
ALLOWED_IPS = os.getenv('ALLOWED_IPS', '').split(',')
print(f"Allowed IPs: {ALLOWED_IPS}")

@app.before_request
def limit_remote_addr():
    if 'X-Forwarded-For' in request.headers:
        user_ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    else:
        user_ip = request.remote_addr

    print(f"Cliente IP: {user_ip}")

    if user_ip not in ALLOWED_IPS:
        print(f"Acesso negado para IP: {user_ip}")
        abort(403)
    else:
        print(f"Acesso permitido para IP: {user_ip}")

# Configura o Google Sheets
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
        nome = request.form.get('nome')
        action = request.form.get('action')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range='Cadastro!A2:A').execute()
        nomes = result.get('values', [])
        nomes = [nome[0] for nome in nomes if nome]
        return render_template('index.html', nomes=nomes, current_time=datetime.datetime.now())

if __name__ == '__main__':
    app.run(debug=True)
