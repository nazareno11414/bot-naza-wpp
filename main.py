from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

INSTANCE_ID = "instance121041"
TOKEN = "nep6e0ap1ru4s6wg"
API_URL = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"

# Para evitar bucles infinitos
RESPONDIDOS = set()

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data or "data" not in data:
        return jsonify({"error": "No se recibió información válida"}), 400

    mensaje_info = data["data"]

    # Extraer información
    numero = mensaje_info.get("from", "").replace("@c.us", "")
    mensaje = mensaje_info.get("body", "")
    tipo = mensaje_info.get("type", "")

    # Evitar responder a mensajes propios o sin número
    if mensaje_info.get("fromMe") or not numero:
        return jsonify({"status": "ignorado"})

    print(f"Mensaje recibido de {numero}: {mensaje}")

    # Evitar responder múltiples veces al mismo mensaje
    msg_id = mensaje_info.get("id")
    if msg_id in RESPONDIDOS:
        return jsonify({"status": "repetido"})
    RESPONDIDOS.add(msg_id)

    # Lógica de respuestas
    if tipo == "text":
        mensaje = mensaje.lower().strip()

        if mensaje == "1":
            respuesta = "✅ Opción 1 seleccionada: Aquí va la info del consorcio."
        elif mensaje == "2":
            respuesta = "📷 Opción 2 seleccionada: Envíe la *foto del comprobante* seguida de la UF y altura.\nEjemplo: UF 12 Altura 4B"
        else:
            respuesta = (
                "📋 *Menú de opciones*\n"
                "1️⃣ Ver datos del consorcio\n"
                "2️⃣ Enviar comprobante de pago\n"
                "Por favor, responda con el número de la opción."
            )

        # Enviar respuesta
        payload = {
            "to": numero,
            "body": respuesta
        }
        headers = {"Content-Type": "application/json"}
        requests.post(API_URL, json=payload, headers=headers)

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
