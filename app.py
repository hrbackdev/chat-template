from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import os
import random
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
ENDPOINT = os.getenv("ENDPOINT")

def generate_session_id():
    return str(random.randint(100000, 999999))

@app.route('/')
def index():
    if "chat_history" not in session:
        session["chat_history"] = []
    if "session_id" not in session:
        session["session_id"] = generate_session_id()
    return render_template("index.html", chat_history=session["chat_history"], session_id=session["session_id"])

@app.route('/send', methods=['POST'])
def send():
    user_message = request.form['message']
    session["chat_history"].append({"role": "user", "text": user_message})

    payload = {
        "user_id": os.getenv("USER_ID"),
        "pregunta": user_message,
        "id_session": session["session_id"],
        "celular": os.getenv("CELULAR"),
        "codigo_asesor": os.getenv("CODIGO_ASESOR"),
        "correo_asesor": os.getenv("CORREO_ASESOR"),
        "status": os.getenv("STATUS"),
        "cod_oficina": os.getenv("COD_OFICINA"),
        "productos": [
            {
                "producto": os.getenv("PRODUCTO"),
                "isIdoneo": os.getenv("IS_IDONEO")
            }
        ]
    }

    try:
        response = requests.post(ENDPOINT, json=payload)
        response.raise_for_status()
        data = response.json()
        assistant_message = data.get("respuesta", "Respuesta no disponible.")
    except Exception as e:
        assistant_message = f"Error al consultar el agente: {e}"

    session["chat_history"].append({"role": "assistant", "text": assistant_message})
    session.modified = True
    return jsonify({"response": assistant_message})

@app.route('/reset', methods=['POST'])
def reset():
    session.pop("chat_history", None)
    session["session_id"] = generate_session_id()
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
