import socket
import struct
import json
import copy
import random


liste_réponses_droles = [
    'aha ez',
    'vasy vasy',
    'cooooll',
    'doucement NALA',
    'accidentttttt',
    'aller feinteeee',
    'le prof est génial',
    'laisse moi gagner',
    'tu es vraiment trop fort ',
    'aha super partie ',
    'merci pour tout'
]


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

    return json.loads(b''.join(chunks).decode("utf-8"))


def send_message(sock, msg):
    msg_bytes = json.dumps(msg).encode("utf-8")
    sock.sendall(struct.pack("I", len(msg_bytes)))
    sock.sendall(msg_bytes)

def actions(state):
    board = state["board"]
    current = state["current"]

    my_kind = "dark" if current == 0 else "light"
    direction = -1 if current == 0 else 1

    tiles = []

    for i in range(8):
        for j in range(8):
            cell = board[i][j][1]
            if cell is not None:
                color, kind = cell
                if kind == my_kind:
                    tiles.append((i, j, color))

    required_color = state["color"]

    if required_color is not None:
        tiles = [t for t in tiles if t[2] == required_color]

    moves = []

    for (i, j, color) in tiles:
        for dj in [-1, 0, 1]:

            ni = i + direction
            nj = j + dj

            while 0 <= ni < 8 and 0 <= nj < 8:

                if board[ni][nj][1] is not None:
                    break

                moves.append([[i, j], [ni, nj]])

                ni += direction
                nj += dj

    return moves

def result(state, move):
    new_state = copy.deepcopy(state)
    board = new_state["board"]

    (i, j), (ni, nj) = move

    piece = board[i][j][1]

    board[i][j][1] = None
    board[ni][nj][1] = piece

    new_state["color"] = board[ni][nj][0]
    new_state["current"] = 1 - new_state["current"]

    return new_state


def is_winner(state):
    board = state["board"]

    for j in range(8):
        cell = board[0][j][1]
        if cell is not None:
            color, kind = cell
            if kind == "dark":
                return True

    for j in range(8):
        cell = board[7][j][1]
        if cell is not None:
            color, kind = cell
            if kind == "light":
                return True

    return False

def evaluate(state):
    if is_winner(state):
        return 10000 if state["current"] == 1 else -10000

    board = state["board"]
    score = 0

    for i in range(8):
        for j in range(8):
            cell = board[i][j][1]

            if cell is not None:
                color, kind = cell

                if kind == "dark":
                    score += (7 - i) * 10
                    if j == 0 or j == 7:
                        score += 3
                else:
                    score -= i * 10

    return score



def minimax(state, depth, maximizing):
    if depth == 0 or is_winner(state):
        return evaluate(state)

    moves = actions(state)

    if not moves:
        return evaluate(state)

    if maximizing:
        best = -999999
        for move in moves:
            new_state = result(state, move)
            score = minimax(new_state, depth - 1, False)
            best = max(best, score)
        return best

    else:
        best = 999999
        for move in moves:
            new_state = result(state, move)
            score = minimax(new_state, depth - 1, True)
            best = min(best, score)
        return best


def best_action(state):
    moves = actions(state)

    best_score = -999999
    best_move = None

    for move in moves:
        new_state = result(state, move)

        score = minimax(new_state, 1, False)  

        (i, j), (ni, nj) = move

        if j == nj:
            score += 5
        else:
            score -= 2

        if is_winner(new_state):
            score += 100000

        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def run_bot():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("192.168.129.65", 3000))

    send_message(s, {
        "request": "subscribe",
        "port": 8889,
        "name": "bot_minimax",
        "matricules": ["24068"]
    })

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8889))
    server.listen()

    while True:
        client, addr = server.accept()
        message = recv_message(client)

        if message is None:
            client.close()
            continue

        if message.get("request") == "ping":
            send_message(client, {"response": "pong"})

        elif message.get("request") == "play":
            state = message["state"]

            move = best_action(state)

            if move is None:
                send_message(client, {"response": "giveup"})
            else:
                send_message(client, {
                    "response": "move",
                    "move": move,
                    "message": random.choice(liste_réponses_droles)
                })

        client.close()

    s.close()


if __name__ == "__main__":
    run_bot()