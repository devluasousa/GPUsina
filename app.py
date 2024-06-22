from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import secrets
import ssl
import httplib2

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Chave secreta para a sessão

# Configura o Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'gestaopontousina-a32a6ea09560.json'

def build_service():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=credentials)

service = build_service()
# ID da sua planilha
SPREADSHEET_ID = '1144zWwPY4atubZ--ZtIabpMeqeIj_0uMOoVXCfPTyTQ'

# Código de confirmação (deve ser gerado e impresso no QR Code)
CONFIRMATION_CODE = "us1n42k240622"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        qr_code_value = request.form.get('qr_code_value')
        if qr_code_value != CONFIRMATION_CODE:
            return render_template('index.html')

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
        try:
            result = service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID, range=range_,
                valueInputOption='USER_ENTERED', body=body).execute()
            return redirect(url_for('success'))
        except Exception as e:
            return render_template('error.html', message="Erro ao registrar ponto: " + str(e))
    else:
        try:
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, range='Cadastro!A2:A').execute()
            nomes = result.get('values', [])
            nomes = [nome[0] for nome in nomes if nome]
            return render_template('index.html', nomes=nomes, current_time=datetime.datetime.now())
        except Exception as e:
            return render_template('error.html', message="Erro ao carregar nomes: " + str(e))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/error')
def error():
    return render_template('error.html', message="Ocorreu um erro. Tente novamente.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
