import socket
import threading
import pyaudio

client = socket.socket()

host = "localhost"
port = 5000

client.connect((host, port))

p = pyaudio.PyAudio()

Format = pyaudio.paInt16
CHANNELS = 2
RATE = 44000
CHUNK = 640

input_stream = p.open(format=Format, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
output_stream = p.open(format=Format, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)


def send():
    while (True):
        try:
            data = input_stream.read(CHUNK)
            client.send(data)
        except:
            break


def receive():
    while (True):
        try:
            data = client.recv(CHUNK)
            output_stream.write(data)
        except:
            break

while True:
    t1 = threading.Thread(target=send)
    t2 = threading.Thread(target=receive)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
