import socket
import threading
import pyaudio
import tkinter as tk
import wave
import numpy as np
import librosa
import io



# Audio constants
CHUNK = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100

# Networking constants
HOST = '127.0.0.1'  # Replace with your server's IP address
PORT = 12345

# Global state for mute control


# Initialize PyAudio

# Function to capture and send audio
class client_handler:
    def __init__(self, host, port):
        self.p = pyaudio.PyAudio()
        self.input_device_index = self.p.get_default_input_device_info()['index']
        self.output_device_index = self.p.get_default_output_device_info()['index']
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        self.conn = client_socket
        self.running = True
        self.root = tk.Tk()
        self.setup_gui()
        self.send_thread = threading.Thread(target=self.send_audio)
        self.receive_thread = threading.Thread(target=self.receive_audio)
        self.is_muted = False
        self.send_thread.start()
        self.voice_change_enabled = False
        self.pitch_factor = 0.0
        self.is_recording = False
        self.recording_thread = None
        self.receive_thread.start()
        self.frames = []
        
        try:
            self.root.mainloop()
        finally:
            self.running = False
            self.conn.close()
            self.p.terminate()
            if self.send_thread.is_alive():
                self.send_thread.join()
            if self.receive_thread.is_alive():
                self.receive_thread.join()
                
    def change_voice(self, data, pitch_factor):
        try:
            audio_data = np.frombuffer(data, dtype=np.float32)
            # 利用 librosa 改变音高
            shifted_audio = librosa.effects.pitch_shift(audio_data, sr=RATE, n_steps=pitch_factor,n_fft=1024)
            # 将 float32 的 numpy 数组转换回字节数据
            return shifted_audio.tobytes()
        except Exception as e:
            print(f"An error occurred in change_voice: {e}")
            # 可以在这里重新抛出异常或者按需处理
            raise
        
    def toggle_voice_change(self):
        self.voice_change_enabled = not self.voice_change_enabled
        # You can define how you want to modify the pitch factor here
        self.pitch_factor = 7 if self.voice_change_enabled else 0.0
        self.voice_change_button.config(text="Disable Voice Change" if self.voice_change_enabled else "Enable Voice Change")

    def send_audio(self):
        stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=self.input_device_index,
                        frames_per_buffer=CHUNK)
        
        while self.running:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                if self.voice_change_enabled:
                    data = self.change_voice(data, pitch_factor=self.pitch_factor)
                if not self.is_muted:
                    self.conn.sendall(data)
                    if self.is_recording:
                        self.frames.append(data)
            except:
                break
        stream.close()
        
    def receive_audio(self):
        stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        output_device_index=self.output_device_index,
                        frames_per_buffer=CHUNK)

        while self.running:
            try:
                data = self.conn.recv(CHUNK)
                stream.write(data)
                if self.is_recording:
                    self.frames.append(data)
            except:
                break

    def save_recording(self):
        with wave.open('recording.wav', 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.frames))
            return
    
    def start_recording(self):
        self.is_recording = True
    
    def stop_recording(self):
        self.is_recording = False
    
    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
            self.record_button.config(text="Start Recording")
        else:
            self.start_recording()
            self.record_button.config(text="Stop Recording")
        
    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.mute_button.config(text="unmute" if self.is_muted else "mute")
        
    def on_closing(self):
        self.running = False
        self.root.destroy()
        self.conn.close()
        if self.frames:
            self.save_recording()
    
    def on_pitch_factor_change(self, value):
        self.pitch_factor = float(value)  # 将滑动条的值转换为浮点数并更新音调因子
        
    def setup_gui(self):
        self.root.title("P2P Voice Chat")
        self.root.geometry("400x300")
        self.mute_button = tk.Button(self.root, text="mute", command=self.toggle_mute)
        self.mute_button.pack(pady=20)
        self.record_button = tk.Button(self.root, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(pady=20)
        self.voice_change_button = tk.Button(self.root, text="Enable Voice Change", command=self.toggle_voice_change)
        self.voice_change_button.pack(pady=20)
        self.pitch_slider = tk.Scale(self.root, from_=-12, to=12, orient='horizontal', label='Pitch Factor', length=300, command=self.on_pitch_factor_change)
        self.pitch_slider.pack(pady=20)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window closing
              
