
import socket
import socketserver
import threading
from collections import deque


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        client = self.request
        address = self.client_address

        print(f"[TCP] Connexion : {address}")

        with self.server.clients_lock:
            self.server.clients.add(client)

        buffer = b""

        try:
            while True:
                data = client.recv(1024)

                if not data:
                    break

                buffer += data

                # Extraction des messages terminés par \n
                while b"\n" in buffer:
                    raw_message, buffer = buffer.split(b"\n", 1)

                    message = raw_message.decode(
                        "utf-8", errors="replace"
                    ).strip()

                    if message:
                        self.server.messages.append(message)
                        print(f"[TCP] Reçu : {message}")

        except OSError as error:
            print(f"[TCP] Erreur : {error}")

        finally:
            with self.server.clients_lock:
                self.server.clients.discard(client)

            print(f"[TCP] Déconnexion : {address}")


class TCPServer:
    def __init__(self, host="0.0.0.0", port=8002):
        self.host = host
        self.port = port

        self.clients = set()
        self.clients_lock = threading.Lock()

        self.messages = deque(maxlen=100)
        
        self.server = socketserver.ThreadingTCPServer(
            (self.host, self.port),
            TCPHandler
        )

        # Les attributs sont accessibles depuis TCPHandler
        self.server.clients = self.clients
        self.server.clients_lock = self.clients_lock
        self.server.messages = self.messages

        self.server.allow_reuse_address = True
        self.server.daemon_threads = True

        self.thread = None

    def start(self):
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True
        )

        self.thread.start()

        print(f"[TCP] Serveur actif sur {self.host}:{self.port}")

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

        print("[TCP] Serveur arrêté")

    def read(self):
        return list(self.messages)

    def write(self, data):
        if not isinstance(data, str) or not data.strip():
            return False

        message = data.strip() + "\n"
        encoded_message = message.encode("utf-8")

        sent = 0

        with self.clients_lock:
            for client in list(self.clients):
                try:
                    client.sendall(encoded_message)
                    sent += 1

                except OSError:
                    self.clients.discard(client)

        return sent > 0

    def is_connected(self):
        with self.clients_lock:
            return len(self.clients) > 0
