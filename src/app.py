
from flask import Flask, jsonify, render_template, request
from TCP import TCPServer

LIMITE_TOF_MIN_AVANT_DETECTION = 250


app = Flask(__name__)

tcp = TCPServer(host="0.0.0.0", port=8002)
tcp.start()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/data", methods=["GET"])
def read_tcp():

    messages = tcp.read()

    # Vérifier qu'un message existe
    if not messages:
        return jsonify({
            "connected": tcp.is_connected(),
            "TOF": None,
            "PIR": None,
            "ON" : None
        })

    # Récupérer le dernier message
    last_message = messages[-1]

    # Extraire les données individuellement
    tof = last_message.get("TOF")
    pir = last_message.get("PIR")
    on = last_message.get("ON")
    
    return jsonify({
        "connected": tcp.is_connected(),
        "TOF": tof,
        "PIR": pir,
        "ON" : on
    })


    


@app.route("/api/command", methods=["POST"])
def write_tcp():

    content = request.get_json(silent=True) or {}
    command = content.get("command")

    if not isinstance(command, str) or not command.strip():
        return jsonify({
            "status": "error",
            "message": "Commande invalide"
        }), 400

    success = tcp.write(command)

    if not success:
        return jsonify({
            "status": "error",
            "message": "Aucune carte connectée"
        }), 503

    return jsonify({
        "status": "success",
        "sent": command
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        use_reloader=False
    )
