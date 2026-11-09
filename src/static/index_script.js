const alarmButton = document.getElementById("alarmButton");
const historyButton = document.getElementById("historyButton");
const historySection = document.getElementById("history");
const historyList = document.getElementById("historyList");
const letterCount = document.getElementById("letterCount");

//mise à jour de l'état de l'alarme
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

//activation et desactivation de l'alarme
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

//affiche les 10 derniers evenements
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
//change dynamiquement l'affichage du nombre de lettre 
async function refreshLetters() {
    try {
        const response = await fetch("/api/letters");
        const data = await response.json();

        letterCount.textContent = data.count;
    } catch (error) {
        letterCount.textContent = "?";
    }
}

//refresh auto (2s pour les lettres et 1s pour l'historique)
refreshLetters();
setInterval(refreshLetters, 2000);
refreshData();
setInterval(refreshData, 1000);