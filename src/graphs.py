import os
import csv
import matplotlib.pyplot as plt
from datetime import datetime

GRAPH_DIR = "graph"


def get_events(filename, event=None):
    path = f"data/{filename}.csv"

    if not os.path.exists(path):
        return []

    with open(path, "r", newline="") as file:
        rows = list(csv.DictReader(file))

    if event is not None:
        rows = [row for row in rows if row["event"] == event]

    dates = []
    for row in rows:
        try:
            dates.append(datetime.fromisoformat(row["date"]))
        except (ValueError, KeyError):
            pass

    return dates


def make_graph(dates, title, filename):
    os.makedirs(GRAPH_DIR, exist_ok=True)

    plt.figure()
    plt.plot(dates, range(1, len(dates) + 1), marker="o")
    plt.xlabel("Temps")
    plt.ylabel("Nombre d'événements cumulés")
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{GRAPH_DIR}/{filename}.png")
    plt.close()


def update_graphs(graph_type):
    if graph_type == "vol":
        dates = get_events("vol")
        make_graph(dates, "Tentatives de vol", "vols")

    elif graph_type == "recuperation":
        dates = get_events("lettres", "Récupération du courrier")
        make_graph(dates, "Récupérations de lettres", "recuperations")

    elif graph_type == "depot":
        dates = get_events("lettres", "Dépôt de lettre")
        make_graph(dates, "Dépôts de lettres", "depots")