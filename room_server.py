import socket
import threading

# Audio constants
CHUNK = 1024

# Networking constants
HOST = '0.0.0.0'
PORT = 12345

# Client handler function
class room_server:
    def __init__(self, host=HOST, port=PORT):
        self.clients = []
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()
        self.host = host
        self.port = port

    def client_handler(self, client_socket):
        while True:
            try:
                data = client_socket.recv(CHUNK)
                for client in self.clients:
                    if client is not client_socket:
                        client.sendall(data)
            except ConnectionResetError:
                break

        # Remove client from list when disconnected
        self.clients.remove(client_socket)
        client_socket.close()

    # Start the server and listen for connections
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print("Server started. Waiting for clients to connect...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Client {addr} connected.")
            self.clients.append(client_socket)
            threading.Thread(target=self.client_handler, args=(client_socket,)).start()
            