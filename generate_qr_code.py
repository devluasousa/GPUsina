import qrcode
import os

# Código de confirmação
SITE_PONTOUSINA = "https://gpusina.onrender.com"

# Verificar o diretório atual
current_directory = os.getcwd()
print(f"Diretório atual: {current_directory}")

# Gerar o QR Code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(SITE_PONTOUSINA)
qr.make(fit=True)

# Criar a imagem do QR Code
img = qr.make_image(fill='black', back_color='white')
img_path = os.path.join(current_directory, "linkqrcode.png")
img.save(img_path)

print(f"QR Code gerado com sucesso e salvo como {img_path}")
