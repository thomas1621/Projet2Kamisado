import socket
import struct
import json
import random
import time

MON_NOM = "bot_minimax"
MON_MATRICULE = "24068"
SERVEUR_IP = "192.168.129.19"

TEMPS_MAX = 2.8

liste_reponses_droles = [
    'aha ez','vasy vasy','cooooll','doucement NALA',
    'accidentttttt','aller feinteeee','le prof est génial',
    'laisse moi gagner','tu es vraiment trop fort ',
    'aha super partie ','merci pour tout'
]

# ---------------- NETWORK ----------------

def recv_message(sock):
    size_data = sock.recv(4)
    if not size_data:
        return None

    size = struct.unpack("I", size_data)[0]

    data = b""
    while len(data) < size:
        packet = sock.recv(1024)
        if not packet:
            break
        data += packet

    return json.loads(data.decode("utf-8"))


def send_message(sock, msg):
    msg_bytes = json.dumps(msg).encode("utf-8")
    sock.sendall(struct.pack("I", len(msg_bytes)))
    sock.sendall(msg_bytes)

# ---------------- PLAYER ----------------

def my_kind(state):
    my_index = state["players"].index(MON_NOM)
    return "dark" if my_index == 0 else "light"

def opponent(kind):
    return "light" if kind == "dark" else "dark"

# ---------------- MOVES ----------------

def action(state, kind):
    board = state["board"]
    required_color = state["color"]

    directions = [(-1,0),(-1,-1),(-1,1)] if kind=="dark" else [(1,0),(1,1),(1,-1)]

    moves = []

    for i in range(8):
        for j in range(8):

            cell = board[i][j][1]
            if cell is None:
                continue

            if cell[1] != kind:
                continue

            if required_color is not None and cell[0] != required_color:
                continue

            for di,dj in directions:
                ni, nj = i+di, j+dj

                while 0<=ni<8 and 0<=nj<8:
                    if board[ni][nj][1] is not None:
                        break

                    moves.append([[i,j],[ni,nj]])
                    ni += di
                    nj += dj

    return moves

# ---------------- PLAY ----------------

def play_move(state, move):
    (i,j),(ni,nj)=move

    piece = state["board"][i][j][1]
    state["board"][i][j][1]=None
    state["board"][ni][nj][1]=piece

    old_color = state["color"]
    state["color"] = state["board"][ni][nj][0]

    return old_color, piece

def undo_move(state, move, old_color, piece):
    (i,j),(ni,nj)=move

    state["board"][ni][nj][1]=None
    state["board"][i][j][1]=piece
    state["color"]=old_color

# ---------------- HEURISTIQUES ----------------

def is_winning_move(move, kind):
    end_row = move[1][0]
    return (kind=="dark" and end_row==0) or (kind=="light" and end_row==7)

def score_move(move, kind):
    (i,j),(ni,nj)=move

    if is_winning_move(move, kind):
        return 10000

    if kind=="dark":
        avance = i - ni
        progress = 7 - ni
    else:
        avance = ni - i
        progress = ni

    return avance*15 + progress*10

def sort_moves(moves, kind):
    return sorted(moves, key=lambda m: score_move(m, kind), reverse=True)

# ---------------- COLOR STRATEGY ----------------

def evaluate_color_control(state, me, opp):
    if state["color"] is None:
        return 0

    forced_color = state["color"]

    my_moves = []
    opp_moves = []

    for m in action(state, me):
        (i,j),(ni,nj)=m
        if state["board"][ni][nj][0] == forced_color:
            my_moves.append(m)

    for m in action(state, opp):
        (i,j),(ni,nj)=m
        if state["board"][ni][nj][0] == forced_color:
            opp_moves.append(m)

    score = 0

    score += len(my_moves) * 30
    score -= len(opp_moves) * 30

    for m in opp_moves:
        if is_winning_move(m, opp):
            score -= 5000

    for m in my_moves:
        if is_winning_move(m, me):
            score += 5000

    return score

# ---------------- EVALUATION ----------------

def evaluate(state, me, opp):
    board = state["board"]

    for j in range(8):
        if board[0][j][1] and board[0][j][1][1]=="dark":
            return 100000 if me=="dark" else -100000
        if board[7][j][1] and board[7][j][1][1]=="light":
            return 100000 if me=="light" else -100000

    score = 0
    centre = [(3,3),(3,4),(4,3),(4,4)]

    for i in range(8):
        for j in range(8):

            cell = board[i][j][1]
            if cell is None:
                continue

            kind = cell[1]
            value = 1 if kind==me else -1

            progress = (7-i) if kind=="dark" else i
            score += value * progress * 10

            if (i,j) in centre:
                score += value * 5

    score += len(action(state, me)) * 2
    score -= len(action(state, opp)) * 2

    score += evaluate_color_control(state, me, opp)

    return score

# ---------------- ANTI BLUNDER ----------------

def opponent_can_win(state, opp):
    for m in action(state, opp):
        if is_winning_move(m, opp):
            return True
    return False

def opponent_can_win_in_two(state, opp, me):
    for m in action(state, opp):
        old_color, piece = play_move(state, m)

        if is_winning_move(m, opp):
            undo_move(state, m, old_color, piece)
            return True

        for m2 in action(state, me):
            old_color2, piece2 = play_move(state, m2)

            for m3 in action(state, opp):
                if is_winning_move(m3, opp):
                    undo_move(state, m2, old_color2, piece2)
                    undo_move(state, m, old_color, piece)
                    return True

            undo_move(state, m2, old_color2, piece2)

        undo_move(state, m, old_color, piece)

    return False

# ---------------- NEGAMAX ----------------

def negamax(state, depth, kind, me, opp, start, alpha, beta):

    if time.time() - start > TEMPS_MAX:
        return evaluate(state, me, opp), True

    moves = action(state, kind)

    if not moves:
        return evaluate(state, me, opp), False

    moves = sort_moves(moves, kind)
    moves = moves[:15]

    best = -float("inf")

    for move in moves:

        if is_winning_move(move, kind):
            return 100000, False

        old_color, piece = play_move(state, move)

        score, timeout = negamax(
            state,
            depth+1,
            opponent(kind),
            me,
            opp,
            start,
            -beta,
            -alpha
        )

        score = -score
        undo_move(state, move, old_color, piece)

        if timeout:
            return best, True

        if score > best:
            best = score

        alpha = max(alpha, score)

        if alpha >= beta:
            break

    return best, False

# ---------------- BEST ACTION ----------------

def best_action(state, kind):

    me = kind
    opp = opponent(kind)

    start = time.time()

    moves = action(state, kind)
    if not moves:
        return None

    moves = sort_moves(moves, kind)

    for m in moves:
        if is_winning_move(m, kind):
            return m

    safe_moves = []

    for m in moves:
        old_color, piece = play_move(state, m)

        if not opponent_can_win(state, opp) and not opponent_can_win_in_two(state, opp, me):
            safe_moves.append(m)

        undo_move(state, m, old_color, piece)

    if safe_moves:
        moves = safe_moves

    moves = moves[:20]

    best_move = moves[0]
    best_score = -float("inf")

    depth = 1

    while True:

        if time.time() - start > TEMPS_MAX:
            break

        for m in moves:

            old_color, piece = play_move(state, m)

            score, timeout = negamax(
                state,
                depth,
                opp,
                me,
                opp,
                start,
                -float("inf"),
                float("inf")
            )

            score = -score
            undo_move(state, m, old_color, piece)

            if timeout:
                break

            if score > best_score:
                best_score = score
                best_move = m

        depth += 1

    return best_move

# ---------------- BOT ----------------

def run_bot():

    s = socket.socket()
    s.connect((SERVEUR_IP, 3000))

    send_message(s, {
        "request": "subscribe",
        "port": 8888,
        "name": MON_NOM,
        "matricules": [MON_MATRICULE]
    })

    server = socket.socket()
    server.bind(("0.0.0.0", 8888))
    server.listen(1)

    while True:

        client, _ = server.accept()
        message = recv_message(client)

        if not message:
            client.close()
            continue

        if message.get("request") == "ping":
            send_message(client, {"response": "pong"})

        elif message.get("request") == "play":

            state = message["state"]
            kind = my_kind(state)

            move = best_action(state, kind)

            if not move:
                send_message(client, {"response": "giveup"})
            else:
                send_message(client, {
                    "response": "move",
                    "move": move,
                    "message": random.choice(liste_reponses_droles)
                })

        client.close()

if __name__ == "__main__":
    run_bot()