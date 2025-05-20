from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Variables de entorno para seguridad
INSTANCE_ID = os.environ.get("ULTRAMSG_INSTANCE_ID")
TOKEN = os.environ.get("ULTRAMSG_TOKEN")
API_URL = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"

def enviar_mensaje(numero, mensaje):
    payload = {
        "token": TOKEN,
        "to": numero,
        "body": mensaje
    }
    response = requests.post(API_URL, data=payload)
    print(f"🔁 UltraMsg Response: {response.status_code} - {response.text}")
    return response

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("==> Data recibida:", data)

    # Extraemos la info del mensaje
    mensaje = data.get("data", {}).get("body")
    numero = data.get("data", {}).get("from")
    from_me = data.get("data", {}).get("fromMe", False)  # <-- FILTRO PARA NO RESPONDER AL PROPIO BOT

    # Evitar bucle infinito: si el mensaje es del propio bot, ignorar
    if from_me:
        print("Mensaje enviado por el bot, no se procesa para evitar bucle.")
        return jsonify({"status": "ignored"}), 200

    if not numero or not mensaje:
        return jsonify({"status": "error", "message": "Missing 'from' or 'body'"}), 400

    # Limpiamos el número para quitar el sufijo '@c.us'
    if numero.endswith("@c.us"):
        numero = numero.replace("@c.us", "")

    mensaje = mensaje.strip().lower()

    if mensaje == "hola":
        respuesta = (
            "1️⃣ Enviar comprobante\n"
            "2️⃣ Consultar estado de cuenta\n"
            "3️⃣ Hablar con un operador\n\n"
            "Por favor, responda con el número de la opción deseada."
        )
        enviar_mensaje(numero, respuesta)

    elif mensaje == "1":
        respuesta = "📸 Por favor, envíe la *foto del comprobante* seguida de la UF y altura.\nEjemplo: UF 12 Altura 4B"
        enviar_mensaje(numero, respuesta)

    elif mensaje == "2":
        respuesta = "💰 Su estado de cuenta se encuentra *al día*. Gracias por su consulta."
        enviar_mensaje(numero, respuesta)

    elif mensaje == "3":
        respuesta = "📞 Será atendido por un operador en breve."
        enviar_mensaje(numero, respuesta)

    else:
        respuesta = "❌ Opción no válida. Por favor, envíe 'Hola' para comenzar."
        enviar_mensaje(numero, respuesta)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
