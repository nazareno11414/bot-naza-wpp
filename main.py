from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    print("==> Data recibida:", data)

    # Verificamos si es un mensaje que el bot mismo envió
    if "data" in data and data["data"].get("fromMe", False):
        print("==> Ignorando mensaje propio para evitar bucle")
        return jsonify({"status": "ignored"}), 200

    mensaje = data.get("body", "")
    numero = data.get("from", "")

    if not numero:
        print("==> No se recibió número")
        return jsonify({"error": "Número no encontrado"}), 400

    print(f"Mensaje recibido de {numero}: {mensaje}")

    # Verificamos si es texto
    if data.get("type") == "text":
        if mensaje.lower() == "comprobante":
            respuesta = "📸 Por favor, envíe la *foto del comprobante* seguida de la UF y altura.\nEjemplo: UF 12 Altura 4B"
        else:
            respuesta = "📝 Bienvenido al bot.\nEscriba *comprobante* para enviar su pago."
    
    # Si es imagen
    elif data.get("type") == "image":
        respuesta = "✅ Imagen recibida correctamente. Gracias."

    else:
        respuesta = "❗ Tipo de mensaje no reconocido."

    # Simulación de envío de mensaje de vuelta (acá podrías llamar a UltraMsg API)
    print(f"==> Enviar a {numero}: {respuesta}")

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
