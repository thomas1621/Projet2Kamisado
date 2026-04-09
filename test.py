import socket
import struct
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("172.17.89.219", 3000))

msg = {
    "request": "subscribe",
    "port": 8888,
    "name": "Thomas",
    "matricules": ["24068", "24104"]
}

msg_bytes = json.dumps(msg).encode()

s.sendall(struct.pack("I", len(msg_bytes)))
s.sendall(msg_bytes)

data = s.recv(4)
response = struct.unpack("I", data)[0]
s.close() 
print("test")