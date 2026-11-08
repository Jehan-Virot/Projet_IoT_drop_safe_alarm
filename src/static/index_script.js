const alarmButton = document.getElementById("alarmButton");
const historyButton = document.getElementById("historyButton");
const historySection = document.getElementById("history");
const historyList = document.getElementById("historyList");

// Mise à jour de l'état de l'alarme
async function refreshData() {
    try {
        const response = await fetch("/api/data");
        const data = await response.json();

        if (data.ON === 1) {
            alarmButton.textContent = "Désactiver l'alarme";
        } else {
            alarmButton.textContent = "Activer l'alarme";
        }

        alarmButton.disabled = data.ON === null;
    } catch (error) {
        alarmButton.textContent = "Serveur indisponible";
        alarmButton.disabled = true;
    }
}

// Envoi de la commande "a"
alarmButton.addEventListener("click", async () => {
    alarmButton.disabled = true;

    try {
        await fetch("/api/command", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ command: "a" })
        });

        setTimeout(refreshData, 300);
    } catch (error) {
        refreshData();
    }
});

// Affichage des 10 derniers événements
historyButton.addEventListener("click", async () => {
    historySection.hidden = !historySection.hidden;

    if (historySection.hidden) {
        historyButton.textContent = "Afficher l'historique";
        return;
    }

    historyButton.textContent = "Masquer l'historique";

    try {
        const response = await fetch("/api/history");
        const events = await response.json();

        historyList.innerHTML = "";

        events.forEach(event => {
            const li = document.createElement("li");
            li.textContent = `${event.date} — ${event.event}`;
            historyList.appendChild(li);
        });
    } catch (error) {
        historyList.innerHTML = "<li>Impossible de charger l'historique.</li>";
    }
});

refreshData();
setInterval(refreshData, 1000);