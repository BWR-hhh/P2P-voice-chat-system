import socket
import json
import threading
import tkinter as tk
from tkinter import simpledialog
import client

HOST = '172.20.10.7'  # The server's hostname or IP address
PORT = 12345        # The port used by the server

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Room Client")

        # Prompt for a username

        # Create a socket connection to the server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        # Start a thread to listen for messages from the server
        self.listen_thread = threading.Thread(target=self.receive_messages)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        # Chat interface
        self.text_area = tk.Text(master, state='disabled')
        self.text_area.pack(pady=10)
        
        self.room_listbox_label = tk.Label(master, text="Available Rooms:")
        self.room_listbox_label.pack()
        self.room_list = tk.Listbox(master)
        self.room_list.pack(pady=5)

        self.room_list_button = tk.Button(master, text="List Rooms", command=self.update_room_list)
        self.room_list_button.pack()

        self.create_room_button = tk.Button(master, text="Create Room", command=self.create_room)
        self.create_room_button.pack()

        self.join_room_button = tk.Button(master, text="Join Room", command=self.join_room)
        self.join_room_button.pack()

        # This will get updated with the name of the room the client joins
        self.room_name = None

    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                # 尝试解析消息为JSON，如果是room_list则进行更新
                try:
                    data = json.loads(message)
                    # 如果数据中有 'room_list' 键，则更新房间列表
                    if 'room_list' in data:
                        self.update_room_list_ui(data['room_list'])
                    elif 'Joined room port' in data:
                        # 如果数据中有 'Joined room port' 键，则连接到房间服务器
                        room_port = data['Joined room port']
                        # 连接到房间服务器
                        self.sock.close()
                        new_client = client.client_handler(HOST, room_port)
                        self.master.destroy()
                    else:
                        # 非房间列表消息，显示在聊天窗口
                        self.display_message(message)
                except json.JSONDecodeError:
                    # 非JSON消息，可能是普通聊天消息
                    self.display_message(message)
            except OSError:
                break

    def send_message(self):
        message = self.msg_entry.get()
        if self.room_name and message:
            # Send message to the server with the room name
            command = json.dumps({'action': 'message', 'room': self.room_name, 'message': message})
            self.sock.send(command.encode('utf-8'))

    def update_room_list(self):
        # 请求房间列表
        command = json.dumps({'action': 'list'})
        self.sock.send(command.encode('utf-8'))
    
    def update_room_list_ui(self, rooms):
        # 在主线程中更新Listbox，以线程安全的方式
        self.room_list.delete(0, tk.END)
        for room in rooms:
            self.room_list.insert(tk.END, room)

    def create_room(self):
        room_name = simpledialog.askstring("Create Room", "Enter room name", parent=self.master)
        if room_name:
            command = json.dumps({'action': 'create', 'room': room_name})
            self.sock.send(command.encode('utf-8'))

    def join_room(self):
        # 从Listbox获取选择的房间
        try:
            selection = self.room_list.curselection()
            room_name = self.room_list.get(selection[0])
            self.room_name = room_name
            command = json.dumps({'action': 'join', 'room': room_name})
            self.sock.send(command.encode('utf-8'))
        except IndexError:
            # 如果没有选择任何房间，则弹出提示
            tk.messagebox.showwarning("Join Room", "Please select a room to join from the list.")

    def display_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.yview(tk.END)
        self.text_area.config(state='disabled')
        
def main():
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()