from flask import Flask, jsonify, render_template, request, send_from_directory
from TCP import TCPServer
from utility import log_event, clear_csv
import json
import csv
import os

MAXIMUM = 260 #maximum du TOF qui sera changer dynamiquement
TOF_HISTORY = []      #historique des 20 dernières mesure pour changer le maximum dynamiquement
READ_HISTORY = None   #attend 5 fois après une detection d'une lettre au cas ou le pir detecte en retard la main
LAST_PROCESSED_MESSAGE = None #juste le dernier message qu'on a lus dans read_tcp pour eviter de traiter plusieurs fois un messages

app = Flask(__name__)

tcp = TCPServer(host="0.0.0.0", port=8002)
tcp.start()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")



@app.route("/api/data", methods=["GET"])
def read_tcp():

    global MAXIMUM, READ_HISTORY
    global TOF_HISTORY, LAST_PROCESSED_MESSAGE

    messages = tcp.read()

    if not messages:
        return jsonify({
            "connected": tcp.is_connected(),
            "TOF": None,
            "PIR": None,
            "ON": None
        })

    last_message = messages[-1]

    if isinstance(last_message, str):
        last_message = json.loads(last_message)

    tof = last_message.get("TOF")
    pir = last_message.get("PIR")
    on = last_message.get("ON")

    #eviter de traiter plusieurs fois le même message
    fingerprint = json.dumps(last_message, sort_keys=True)

    if fingerprint != LAST_PROCESSED_MESSAGE:
        LAST_PROCESSED_MESSAGE = fingerprint
        
        #VOLS
        if on == 1 and pir == 1:
            log_event("vol", "Tentative de vol", last_message)
            update_graphs("vol")
            READ_HISTORY = None

        #detection des depots
        elif READ_HISTORY is not None:
            READ_HISTORY.append(last_message)
            if pir == 1:
                log_event("vol", "Tentative de vol", last_message)
                update_graphs("vol")
                READ_HISTORY = None

            elif len(READ_HISTORY) >= 5:
                log_event("pile", "Dépôt de lettre", last_message)
                log_event("lettres", "Dépôt de lettre", last_message)
                update_graphs("depot")
                READ_HISTORY = None

        #nouveau depots
        elif tof is not None and 40 < tof < 0.5 * MAXIMUM:
            READ_HISTORY = []

        #recuperation du courrier dans la boite
        elif tof is None or tof == 0 or tof > MAXIMUM:
            clear_csv("pile") #si la boite est vide on retire la pile
            log_event("lettres", "Récupération du courrier", last_message)
            update_graphs("recuperation")

        #changer le maximum du TOF
        TOF_HISTORY.append(last_message)
        if len(TOF_HISTORY) > 20:
            TOF_HISTORY.pop(0)
        valid_tof = [int(msg["TOF"]) for msg in TOF_HISTORY if msg.get("TOF") is not None and int(msg["TOF"]) > 0] #on prend la valeur la plus élevé des 20 dernières valeurs
        if valid_tof:
            MAXIMUM = max(valid_tof)

    return jsonify({
        "connected": tcp.is_connected(),
        "TOF": tof,
        "PIR": pir,
        "ON": on
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
    
    
@app.route("/api/history")
def get_history():
    events = []

    for filename in ["vol", "lettres"]:
        path = f"data/{filename}.csv"

        if os.path.exists(path):
            with open(path, "r", newline="") as file:
                events.extend(csv.DictReader(file))

    events.sort(key=lambda x: x["date"], reverse=True)

    return jsonify(events[:10])


@app.route("/graph/<filename>")
def graph_file(filename):
    return send_from_directory("graph", filename)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        use_reloader=False
    )
