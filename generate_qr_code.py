import qrcode

# Código de confirmação
CONFIRMATION_CODE = "us1n42k240622"

# Gerar o QR Code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(CONFIRMATION_CODE)
qr.make(fit=True)

# Criar a imagem do QR Code
img = qr.make_image(fill='black', back_color='white')
img.save("confirmation_code_qr.png")

print("QR Code gerado com sucesso e salvo como confirmation_code_qr.png")
