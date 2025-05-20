from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Tu info de UltraMsg
INSTANCE_ID = "instance121041"
TOKEN = "nep6e0ap1ru4s6wg"
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

    mensaje = data.get("data", {}).get("body")
    numero = data.get("data", {}).get("from")

    if not numero or not mensaje:
        return jsonify({"status": "error", "message": "Missing 'from' or 'body'"}), 400

    # Eliminar dominio "@c.us" si lo tiene
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
    app.run(port=10000)
