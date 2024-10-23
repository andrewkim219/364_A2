import ssl
import select
import socket
import sys
import signal
import argparse

from database import initialize_db, authenticate_user
from utils import *

SERVER_HOST = 'localhost'

class ChatServer(object):
    """ An example chat server using select """

    def __init__(self, port, backlog=5):
        self.clients = 0
        self.clientmap = {}
        self.outputs = []  # list output sockets

        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")
        self.context.load_verify_locations('cert.pem')
        self.context.set_ciphers('AES128-SHA')

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port))
        self.server.listen(backlog)
        self.server = self.context.wrap_socket(self.server, server_side=True)
        # Catch keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)

        print(f'Server listening to port: {port} ...')

    def sighandler(self, signum, frame):
        """ Clean up client outputs"""
        print('Shutting down server...')

        # Close existing client sockets
        for output in self.outputs:
            output.close()

        self.server.close()

    def get_client_username(self, client):
        """ Return just the username of the client """
        return self.clientmap[client][1]  # Return only the username

    def get_client_name(self, client):
        """ Return the name of the client """
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))

    def run(self):
        inputs = [self.server]
        self.outputs = []
        running = True
        while running:
            try:
                readable, writeable, exceptional = select.select(inputs, self.outputs, [])
            except select.error as e:
                print(f'Select error: {e}')
                break

            for sock in readable:
                sys.stdout.flush()
                if sock == self.server:
                    client, address = self.server.accept()
                    print(f'Chat server: got connection {client.fileno()} from {address}')
                    username = receive(client)  # Read username
                    password = receive(client)  # Read password

                    if authenticate_user(username, password):
                        send(client, f'CLIENT: {str(address[0])}')
                        inputs.append(client)
                        self.clientmap[client] = (address, username)
                        msg = f'\n(Connected: New client ({self.clients}) from {self.get_client_name(client)})'
                        for output in self.outputs:
                            send(output, msg)
                        self.outputs.append(client)
                    else:
                        send(client, "Authentication failed.")
                        client.close()
                else:
                    # handle all other sockets
                    try:
                        data = receive(sock)
                        if data:
                            # Send as new client's message...
                            msg = f'\n{self.get_client_username(sock)}: {data}'

                            # Send data to all except ourself
                            for output in self.outputs:
                                if output != sock:
                                    send(output, msg)
                        else:
                            print(f'Chat server: {sock.fileno()} hung up')
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)

                            # Sending client leaving information to others
                            msg = f'\n(Now hung up: Client {self.get_client_name(sock)})'

                            for output in self.outputs:
                                send(output, msg)
                    except socket.error as e:
                        print(f'Socket error: {e}')
                        inputs.remove(sock)
                        self.outputs.remove(sock)
                        sock.close()

        self.server.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Socket Server Example with Select')
    parser.add_argument('--name', action="store", dest="name", required=True)
    parser.add_argument('--port', action="store", dest="port", type=int, required=True)
    given_args = parser.parse_args()
    port = given_args.port
    name = given_args.name

    initialize_db()

    server = ChatServer(port)
    server.run()