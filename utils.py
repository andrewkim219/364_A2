import socket
import pickle
import struct


def send(channel, *args):
    """Send a pickled message over a channel"""
    buffer = pickle.dumps(args)
    value = socket.htonl(len(buffer))
    size = struct.pack("L", value)
    channel.send(size)
    channel.send(buffer)


def receive(channel):
    """Receive and unpickle a message from a channel"""
    size = struct.calcsize("L")
    size = channel.recv(size)

    try:
        size = socket.ntohl(struct.unpack("L", size)[0])
    except struct.error as e:
        return ''

    buf = ""
    while len(buf) < size:
        buf += channel.recv(size - len(buf)).decode('utf-8')

    return pickle.loads(buf)[0]
