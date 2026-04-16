import socket
import struct
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("172.17.10.46", 3000))

def recv_message(sock):
    size_data = sock.recv(4)
    if not size_data:
        return None
    size = struct.unpack("I", size_data)[0]
    chunks = []
    received = 0
    while received < size:
        data = sock.recv(1024)
        chunks.append(data)
        received += len(data)
    full_data = b''.join(chunks)
    return json.loads(full_data.decode("utf-8"))

def send_message(sock,msg):
    msg_bytes = json.dumps(msg).encode("utf-8")
    sock.sendall(struct.pack("I", len(msg_bytes)))
    sock.sendall(msg_bytes)

# subscribe
send_message(s,{
    "request": "subscribe",
    "port": 8888,
    "name": "Thomas",
    "matricules": ["24068", "24104"]
})
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 8888))
server.listen()


while True:
    client, addr = server.accept()
    message = recv_message(client)

    if message is None:
        break

    print(message)

    if message.get("request") == "ping":
        send_message(client,{
            "response": "pong"
        })
    client.close()
s.close()