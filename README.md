# P2P-voice-chat-system

This is a peer-to-peer (P2P) voice chat application that allows users to create and join chat rooms, send and receive audio, and perform various audio manipulations such as voice changing and recording.

## Features

- Create and join chat rooms
- Send and receive audio in real-time
- Mute/unmute audio
- Change voice pitch
- Record audio and save as WAV file

## Requirements

- Python 3.x
- tkinter
- pyaudio
- numpy
- librosa
- wave

## Installation

1. Clone the repository:
```
git clone https://github.com/BWR-hhh/P2P-voice-chat-system.git
```
2. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

1. Start the server:
```
python server.py
```
2. Run the client application:
```
python user.py
```
3. Enter a username when prompted.

4. Use the GUI to create or join a chat room.

5. Once in a chat room, you can:
- Mute/unmute your audio using the "Mute" button
- Start/stop recording using the "Start Recording" button
- Enable/disable voice change using the "Enable Voice Change" button
- Adjust the pitch factor using the slider

6. To save a recording, simply close the application window. The recording will be saved as `recording.wav` in the same directory.

## File Structure

- `server.py`: The main server script that handles client connections and manages chat rooms.
- `room_server.py`: The script for the individual room servers that handle audio communication within each chat room.
- `user.py`: The client application script that provides the user interface and handles audio capture and playback.
- `client.py`: The script containing the client-side logic for audio communication and GUI interactions.

## Notes

- Make sure to update the `HOST` and `PORT` variables in the scripts to match your network configuration. (especially for server.py & user.py)
- The application uses the default input and output audio devices. If you want to use different devices, modify the `input_device_index` and `output_device_index` variables in the `client_handler` class in `client.py`.

## Acknowledgements

- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) - Audio I/O library
- [librosa](https://librosa.org/) - Audio processing library
- [NumPy](https://numpy.org/) - Numerical computing library
- [tkinter](https://docs.python.org/3/library/tkinter.html) - Python standard GUI package
