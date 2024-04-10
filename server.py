import socket
import threading
import json
import room_server

HOST = '172.20.10.6'  # Standard loopback interface address (localhost)
PORT = 12345        # Port to listen on (non-privileged ports are > 1023)

chat_rooms = {}  # Dictionary to store chat room information
ROOM_PORT = 12346
room_ports = {}

# Client handler function
def handle_client(conn, addr):
    print(f"New connection from {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            # Decode the received data
            command = json.loads(data.decode())

            if command['action'] == 'create':
                room_name = command['room']
                if room_name not in chat_rooms:
                    chat_rooms[room_name] = []
                    global ROOM_PORT
                    room_server.room_server(HOST, ROOM_PORT)
                    room_ports[room_name] = ROOM_PORT
                    ROOM_PORT += 1
                    conn.sendall(f"Room '{room_name}' created.".encode())
                else:
                    conn.sendall(f"Room '{room_name}' already exists.".encode())

            elif command['action'] == 'list':
                room_list = list(chat_rooms.keys())
                # 将房间列表编码为JSON字符串并发送
                response = json.dumps({'room_list': room_list})
                conn.sendall(response.encode())

            elif command['action'] == 'join':
                room_name = command['room']
                if room_name in chat_rooms:
                    chat_rooms[room_name].append(conn)
                    port = room_ports[room_name]
                    response = json.dumps({'Joined room port': port})
                    conn.sendall(response.encode())
                else:
                    conn.sendall(f"Room '{room_name}' does not exist.".encode())

            elif command['action'] == 'message':
                room_name = command['room']
                message = command['message']
                if conn in chat_rooms.get(room_name, []):
                    for c in chat_rooms[room_name]:
                        if c != conn:
                            c.sendall(f"{addr}: {message}".encode())
    finally:
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server started on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == '__main__':
    main()