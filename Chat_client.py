import ssl

import select
import socket
import sys
import argparse
import threading

from utils import *

SERVER_HOST = 'localhost'
stop_thread = False

def get_and_send(client):
    while not stop_thread:
        data = sys.stdin.readline().strip()
        if data:
            sys.stdout.write('\033[F')
            sys.stdout.write('\r')
            sys.stdout.write(' ' * 80)
            sys.stdout.write('\r')
            sys.stdout.flush()

            # Send the message to the server
            send(client.sock, data)

            # Display the sent message with proper formatting
            sys.stdout.write(f'\rMe: {data}\n')

            # Show the prompt again after sending the message
            sys.stdout.write(client.prompt)
            sys.stdout.flush()

class ChatClient:
    """ A command line chat client using select """

    def __init__(self, name, port, host=SERVER_HOST):
        self.name = name
        self.connected = False
        self.host = host
        self.port = port

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context.set_ciphers('AES128-SHA')

        # Initial prompt
        self.prompt = '>> '

        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print(f'Now connected to chat server@ port {self.port}')
            self.connected = True
            username = input("Enter your username: ")

            # Send my name...
            send(self.sock, username)
            data = receive(self.sock)

            # Contains client address, set it
            addr = data.split('CLIENT: ')[1]

            # Start thread to read user input and send to server
            threading.Thread(target=get_and_send, args=(self,)).start()

        except socket.error as e:
            print(f'Failed to connect to chat server @ port {self.port}')
            sys.exit(1)

    def cleanup(self):
        """Close the connection and wait for the thread to terminate."""
        self.sock.close()



    def run(self):
        """ Chat client main loop """
        # Show the initial prompt when the client starts
        sys.stdout.write(self.prompt)
        sys.stdout.flush()

        while self.connected:
            try:
                # Wait for input from stdin and socket
                readable, _, _ = select.select([self.sock], [], [])

                for sock in readable:
                    if sock == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print('Client shutting down.')
                            self.connected = False
                            break
                        else:
                            sys.stdout.write('\033[F')
                            sys.stdout.flush()

                            sys.stdout.write(f'{data}\n')

                            sys.stdout.write(self.prompt)
                            sys.stdout.flush()

            except KeyboardInterrupt:
                print("Client interrupted.")
                global stop_thread
                stop_thread = True
                self.cleanup()
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', action="store", dest="name", required=True)
    parser.add_argument('--port', action="store", dest="port", type=int, required=True)
    given_args = parser.parse_args()

    port = given_args.port
    name = given_args.name

    client = ChatClient(name=name, port=port)
    client.run()
