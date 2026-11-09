
import os
import csv
from datetime import datetime


def log_event(filename, event, data=None):
    os.makedirs("data", exist_ok=True)
    path = f"data/{filename}.csv"
    fields = ["date", "event", "TOF", "PIR", "ON"]

    row = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "event": event,
        "TOF": (data or {}).get("TOF"),
        "PIR": (data or {}).get("PIR"),
        "ON": (data or {}).get("ON")
    }

    with open(path, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(row)
    trim_csv(filename)


def clear_csv(filename):
    os.makedirs("data", exist_ok=True)
    path = f"data/{filename}.csv"
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["date", "event", "TOF", "PIR", "ON"])


def trim_csv(filename, max_rows=500):
    path = f"data/{filename}.csv"
    
    if not os.path.exists(path):
        return
    
    with open(path, "r", newline="") as file:
        rows = list(csv.reader(file))
        
    if len(rows) <= max_rows + 1: 
        return
    
    header = rows[0]
    recent_rows = rows[-max_rows:]
    
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(recent_rows)
        
        
import csv
import os

def count_letters():
    path = "data/lettres.csv"
    if not os.path.exists(path):
        return 0
    
    with open(path, "r", newline="") as file:
        events = list(csv.DictReader(file))
    events.sort(key=lambda x: x["date"])
    
    count = 0
    for event in events:
        if event["event"] == "Dépôt de lettre":
            count += 1

        elif event["event"] == "Récupération du courrier":
            count = 0

    return count