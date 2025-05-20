from flask import Flask, request, jsonify
import os
import requests
import re
import time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# UltraMsg config
INSTANCE_ID = os.environ.get("ULTRAMSG_INSTANCE_ID")
TOKEN = os.environ.get("ULTRAMSG_TOKEN")
API_URL = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"

# Google Drive config
SERVICE_ACCOUNT_FILE = '/etc/secrets/bot-whatsapp-comprobantes-c2ba3502495c.json'
DRIVE_FOLDER_ID = '1_Ga4XFmGEPvaAfkHENpXAhkVdA4IP9wD'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

# Estados por usuario
estado_usuarios = {}

def enviar_mensaje(numero, mensaje):
    payload = {
        "token": TOKEN,
        "to": numero,
        "body": mensaje
    }
    response = requests.post(API_URL, data=payload)
    print(f"🔁 UltraMsg Response: {response.status_code} - {response.text}")
    return response

def subir_a_drive(nombre_local, nombre_en_drive, carpeta_id=DRIVE_FOLDER_ID):
    file_metadata = {
        'name': nombre_en_drive,
        'parents': [carpeta_id]
    }
    media = MediaFileUpload(nombre_local, resumable=True)
    archivo = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"✅ Archivo subido: {nombre_en_drive}")
    return archivo.get('id')

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("==> Data recibida:", data)

    mensaje = data.get("data", {}).get("body", "")
    numero = data.get("data", {}).get("from", "")
    tipo = data.get("data", {}).get("type", "")
    from_me = data.get("data", {}).get("fromMe", False)

    if from_me or not numero:
        return jsonify({"status": "ignored"}), 200

    if numero.endswith("@c.us"):
        numero = numero.replace("@c.us", "")

    mensaje = mensaje.strip()
    estado = estado_usuarios.get(numero, {"estado": None})

    if tipo == "chat":
        msg_lower = mensaje.lower()

        if msg_lower == "hola":
            respuesta = (
                "1️⃣ Enviar comprobante\n"
                "2️⃣ Consultar estado de cuenta\n"
                "3️⃣ Hablar con un operador\n\n"
                "Por favor, responda con el número de la opción deseada."
            )
            estado_usuarios[numero] = {"estado": None}
            enviar_mensaje(numero, respuesta)

        elif msg_lower == "1":
            respuesta = (
                "📸 Por favor, envíe la *foto o fotos del comprobante*, seguidas de su UF o departamento "
                "y la altura del edificio.\n\n"
                "Ejemplos:\n• UF2 - SM320\n• 3ºA - S254"
            )
            estado_usuarios[numero] = {"estado": "esperando_datos"}
            enviar_mensaje(numero, respuesta)

        elif msg_lower == "2":
            enviar_mensaje(numero, "💰 Su estado de cuenta se encuentra *al día*. Gracias por su consulta.")

        elif msg_lower == "3":
            enviar_mensaje(numero, "📞 Será atendido por un operador en breve.")

        elif estado["estado"] == "esperando_datos":
            patron = re.compile(r"(UF\d+|\d+º[A-Z])\s*-\s*[A-Z]+\d+", re.IGNORECASE)
            if patron.match(mensaje):
                estado_usuarios[numero] = {
                    "estado": "esperando_archivos",
                    "datos": mensaje.replace(" ", "_"),
                    "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                    "contador": 1
                }
                enviar_mensaje(numero, "✅ Datos validados. Ahora puede enviar sus comprobantes (imagen o PDF).")
            else:
                enviar_mensaje(numero, "❌ Formato inválido. Envíe como: UF2 - SM320 o 3ºA - S254")

        else:
            enviar_mensaje(numero, "❌ Opción no válida. Escriba 'Hola' para comenzar.")

    elif tipo in ["image", "document"] and estado.get("estado") == "esperando_archivos":
        url = data["data"].get("media") or data["data"].get("url")

        if not url:
            enviar_mensaje(numero, "❌ No pude obtener el enlace del archivo. Intente reenviar la imagen o PDF.")
            print("📎 La clave 'media/url' vino vacía:", data["data"])
            return jsonify({"status": "ok"}), 200

        extension = ".jpg" if tipo == "image" else ".pdf"
        datos = estado["datos"]
        timestamp = estado["timestamp"]
        contador = estado["contador"]

        filename = f"{datos}_{timestamp}_{contador}{extension}"
        filepath = os.path.join("temp", filename)
        os.makedirs("temp", exist_ok=True)

        try:
            r = requests.get(url)
            r.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(r.content)

            subir_a_drive(filepath, filename)
            enviar_mensaje(numero, f"✅ Archivo recibido y subido en la brevedad le aplicaremos el pago")
            estado_usuarios[numero]["contador"] += 1

        except Exception as e:
            enviar_mensaje(numero, "❌ Error al procesar el archivo.")
            print("❌ Error al descargar o subir archivo:", e)

    else:
        print("📎 Mensaje ignorado o fuera de flujo.")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
