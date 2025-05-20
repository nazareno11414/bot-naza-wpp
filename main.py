from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configuración de UltraMsg
INSTANCE_ID = os.getenv("INSTANCE_ID", "TU_INSTANCE_ID")
TOKEN = os.getenv("TOKEN", "TU_TOKEN_ULTRAMSG")
API_URL = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"

# Menú principal
MENU = """📋 *Menú de opciones*
1️⃣ Enviar comprobante
2️⃣ Consultar saldo
3️⃣ Hablar con un operador
Responde con el número de la opción."""

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    # Extraer información básica
    try:
        numero = data.get("from", "").replace("@c.us", "")
        mensaje = data.get("body", "").strip().lower()
    except:
        print("==> No se recibió número o mensaje")
        return jsonify({"status": "error"}), 400

    print(f"Mensaje recibido de {numero}: {mensaje}")

    # Lógica de respuestas
    if mensaje in ["hola", "menú", "menu", "buenas"]:
        enviar_mensaje(numero, MENU)
    elif mensaje == "1":
        enviar_mensaje(numero, "📸 Por favor, envíe la *foto del comprobante* seguida de la UF y altura.\nEjemplo: UF 12 Altura 4B")
    elif mensaje == "2":
        enviar_mensaje(numero, "💰 Su saldo actual es de $12.345,67")
    elif mensaje == "3":
        enviar_mensaje(numero, "👤 Un operador se comunicará con usted pronto.")
    else:
        enviar_mensaje(numero, "❌ Opción no válida. Por favor elija una opción del menú:\n" + MENU)

    return jsonify({"status": "ok"}), 200

def enviar_mensaje(numero, mensaje):
    payload = {
        "token": TOKEN,
        "to": numero,
        "body": mensaje
    }

    try:
        response = requests.post(API_URL, data=payload)
        print(f"Mensaje enviado a {numero}: {mensaje}")
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
