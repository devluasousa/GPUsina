from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import secrets
import json
import pytz

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Chave secreta para a sessão

# Carregar credenciais do Google a partir da variável de ambiente
def get_google_credentials():
    credentials_info = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    credentials = Credentials.from_service_account_info(credentials_info)
    return credentials

def build_service():
    credentials = get_google_credentials()
    return build('sheets', 'v4', credentials=credentials)

service = build_service()
# ID da sua planilha
SPREADSHEET_ID = '1144zWwPY4atubZ--ZtIabpMeqeIj_0uMOoVXCfPTyTQ'

# Código de confirmação (deve ser gerado e impresso no QR Code)
CONFIRMATION_CODE = "us1n42k240622"

# Define o fuso horário desejado
LOCAL_TIMEZONE = pytz.timezone('America/Sao_Paulo')  # Altere para o fuso horário correto

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        qr_code_value = request.form.get('qr_code_value')
        if qr_code_value != CONFIRMATION_CODE:
            return render_template('index.html')

        nome = request.form.get('nome')
        action = request.form.get('action')

        # Converte a hora atual para o fuso horário desejado
        now_utc = datetime.datetime.now(pytz.utc)
        now_local = now_utc.astimezone(LOCAL_TIMEZONE)
        now_str = now_local.strftime("%Y-%m-%d %H:%M:%S")

        range_ = 'Registros!A2:C'
        values = [
            [now_str, nome, action]
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
            return render_template('index.html', nomes=nomes, current_time=datetime.datetime.now(LOCAL_TIMEZONE))
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
