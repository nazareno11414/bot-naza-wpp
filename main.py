from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Estado por número: guarda en qué parte del flujo está cada persona
estado_usuario = {}

# Tu token e ID de instancia UltraMsg
INSTANCE_ID = "instance121041"
TOKEN = "nep6e0ap1ru4s6wg"

# Enviar mensaje
def enviar_mensaje(to, mensaje):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    params = {
        "token": TOKEN,
        "to": to,
        "body": mensaje
    }
    requests.get(url, params=params)

# Descargar archivo de imagen
def descargar_imagen(url_archivo, nombre_archivo="comprobante.jpg"):
    r = requests.get(url_archivo)
    with open(nombre_archivo, "wb") as f:
        f.write(r.content)

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    numero = data.get("from")
    mensaje = data.get("body", "")
    tipo = data.get("type")

    if not numero:
        return jsonify({"status": "sin número"}), 200

    estado = estado_usuario.get(numero, "inicio")

    if estado == "inicio":
        menu = (
            "👋 Bienvenido al celu de Naza\n"
            "Elija una opción:\n\n"
            "1️⃣ Mandar comprobante\n"
            "(responda solo con el número)"
        )
        enviar_mensaje(numero, menu)
        estado_usuario[numero] = "esperando_opcion"

    elif estado == "esperando_opcion":
        if mensaje.strip() == "1":
            enviar_mensaje(
                numero,
                "📸 Por favor, envíe la *foto del comprobante* seguida de la UF y altura.\nEjemplo: UF 12 Altura 4B"
            )
            estado_usuario[numero] = "esperando_comprobante"
        else:
            enviar_mensaje(numero, "❌ Opción no válida. Por favor, elija una opción del menú (1).")

    elif estado == "esperando_comprobante":
        if tipo == "image":
            url_imagen = data.get("media", {}).get("url")
            caption = data.get("caption", "")
            if url_imagen:
                descargar_imagen(url_imagen, f"{numero}_comprobante.jpg")
                print(f"🖼️ Imagen descargada para {numero} con texto: {caption}")
                enviar_mensaje(numero, "✅ Comprobante recibido. ¡Gracias!")
                estado_usuario[numero] = "inicio"
            else:
                enviar_mensaje(numero, "⚠️ No pude obtener la imagen. Intente de nuevo.")
        else:
            enviar_mensaje(numero, "📷 Por favor, envíe una *imagen* con el texto: UF y altura.")

    return jsonify({"status": "ok"}), 200

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
