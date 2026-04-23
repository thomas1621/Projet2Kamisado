import socket
import struct
import json
import random
liste_réponses_droles = ['aha ez','vasy vasy','cooooll','doucement NALA','accidentttttt','aller feinteeee','le prof est génial','laisse moi gagner','tu es vraiment trop fort ','aha super partie ','merci pour tout']
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
    "name": "anto ",
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

def get_random_move(state, tiles):
    board = state["board"]
    current = state["current"]

    direction = -1 if current == 0 else 1
    possible_moves = []

    for (i, j, color) in tiles:

        for dj in [-1, 0, 1]:
            ni, nj = i, j

            for _ in range(8):
                ni += direction
                nj += dj

                # hors plateau
                if not (0 <= ni < 8 and 0 <= nj < 8):
                    break

                # bloqué par une pièce
                if board[ni][nj][1] is not None:
                    break

                possible_moves.append([[i, j], [ni, nj]])

    print(possible_moves)
    return random.choice(possible_moves) if possible_moves else None
def couleur_to_play(tiles, state):
    required_color = state["color"]

    if required_color is None:
        return tiles
    return [tile for tile in tiles if tile[2] == required_color]
    


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
    elif message.get("request") == "play":
        state = message["state"]
        tiles = couleur_to_play(my_piece(state), state)
        move = get_random_move(state, tiles)

        if move is None:
            send_message(client, {
                "response": "giveup"
            })
        else:
            send_message(client, {
                "response": "move",
                "move": move,
                "message": random.choice(liste_réponses_droles)
            })
    client.close()
s.close()
