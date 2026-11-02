
async function refreshData() {

    try {
        const response = await fetch("/api/data");
        const result = await response.json();

        document.getElementById("status").textContent =
            result.connected ? "Connecté" : "Déconnecté";

        document.getElementById("data").textContent =
            result.messages.length > 0
                ? result.messages.slice(-5).join("\n")
                : "Aucune donnée reçue.";

    } catch (error) {

        document.getElementById("status").textContent =
            "Erreur de connexion au serveur";
    }
}


async function sendCommand() {

    const input = document.getElementById("command");
    const command = input.value.trim();

    if (!command) return;

    try {

        const response = await fetch("/api/command", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                command: command
            })
        });

        const result = await response.json();

        document.getElementById("result").textContent =
            result.status === "success"
                ? "Commande envoyée : " + command
                : "Erreur : " + result.message;

        if (response.ok) {
            input.value = "";
        }

    } catch (error) {

        document.getElementById("result").textContent =
            "Erreur de communication.";
    }
}


// Actualisation immédiate
refreshData();

// Actualisation automatique toutes les secondes
setInterval(refreshData, 1000);
