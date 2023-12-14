import socket
import threading
import pyaudio

class AudioServer:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = []

    def start(self):
        while True:
            client_socket, addr = self.server.accept()
            self.clients.append(client_socket)
            print("Client connected:", addr)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                for client in self.clients:
                    if client != client_socket:
                        client.send(data)
        except:
            self.clients.remove(client_socket)
            client_socket.close()
            print("Client disconnected")

class AudioClient:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.p = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.chunks = 4096
        self.channels = 2
        self.rate = 44100

    def start(self):
        input_stream = self.p.open(format=self.format,
                                   channels=self.channels,
                                   rate=self.rate,
                                   input=True,
                                   frames_per_buffer=self.chunks)

        output_stream = self.p.open(format=self.format,
                                    channels=self.channels,
                                    rate=self.rate,
                                    output=True,
                                    frames_per_buffer=self.chunks)

        send_thread = threading.Thread(target=self.send, args=(input_stream,))
        receive_thread = threading.Thread(target=self.receive, args=(output_stream,))

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

        input_stream.stop_stream()
        input_stream.close()
        output_stream.stop_stream()
        output_stream.close()
        self.p.terminate()

    def send(self, input_stream):
        while True:
            try:
                data = input_stream.read(self.chunks)
                self.client.send(data)
            except:
                break

    def receive(self, output_stream):
        while True:
            try:
                data = self.client.recv(self.chunks)
                output_stream.write(data)
            except:
                print("Not Getting Data So Breaking System")
                break

if __name__ == "__main__":
    server = AudioServer("0.0.0.0", 5000)
    client = AudioClient("localhost", 5000)

    server_thread = threading.Thread(target=server.start)
    client_thread = threading.Thread(target=client.start)

    server_thread.start()
    client_thread.start()

    server_thread.join()
    client_thread.join()
