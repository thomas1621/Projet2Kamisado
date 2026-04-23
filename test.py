import socket
import struct
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("172.17.10.125", 3000))

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

def my_piece(state):
    board = state["board"]
    current = state["current"]

    # joueur 0 → dark
    # joueur 1 → light
    my_kind = "dark" if current == 0 else "light"

    tiles = []

    for i in range(8):
        for j in range(8):
            cell = board[i][j]
            tile = cell[1]

            if tile is not None:
                color, kind = tile
                if kind == my_kind:
                    tiles.append((i, j, color))

    return tiles
import random

def get_random_move(state):
    board = state["board"]
    tiles = my_piece(state)
    current = state["current"]

    direction = -1 if current == 0 else 1  # haut ou bas

    possible_moves = []

    for (i, j, color) in tiles:

        # directions : tout droit, diagonale gauche, diagonale droite
        for dj in [-1, 0, 1]:
            ni = i + direction
            nj = j + dj

            if 0 <= ni < 8 and 0 <= nj < 8:
                if board[ni][nj][1] is None:  # case libre
                    possible_moves.append([[i, j], [ni, nj]])

    if possible_moves:
        return random.choice(possible_moves)
    else:
        return None
def couleur_to_play(tiles, state):
    required_color = state["color"]

    if required_color is None:
        return tiles

    return [t for t in tiles if t[2] == required_color]
    


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
    if message.get("request") == "play":
        state = message["state"]
        tiles = couleur_to_play(my_piece(state),state)
        move = get_random_move(state)

    if move is None:
        send_message(client, {
            "response": "giveup"
        })
    else:
        send_message(client, {
            "response": "move",
            "move": move,
            "message": "Random move"
        })
    move = get_random_move(state)

    if move is None:
        send_message(client, {
            "response": "giveup"
        })
    else:
        send_message(client, {
            "response": "move",
            "move": move,
            "message": "Random move"
        })  
    client.close()
s.close()
