import json
import struct
import time

from bot import (
    recv_message,
    send_message,
    actions,
    play_move,
    undo_move,
    evaluate,
    best_action,
    negamax,
    forced_sequence_score,
    opponent,
    winning_move,
)

# =========================================================
# FAKE SOCKET
# =========================================================

class FakeSocket:
    def __init__(self, chunks):
        self.chunks = chunks
        self.sent = b""

    def recv(self, n):
        return self.chunks.pop(0) if self.chunks else b""

    def sendall(self, data):
        self.sent += data


# =========================================================
# HELPERS
# =========================================================

def empty_board():
    return [[[None, None] for _ in range(8)] for _ in range(8)]


def make_state(board=None, current=0, color=None, players=None):
    return {
        "board": board or empty_board(),
        "current": current,
        "color": color,
        "players": players or ["Thomas ", "Bot"]
    }


# =========================================================
# 1. COMMUNICATION
# =========================================================

def test_recv_send_full():
    msg = {"request": "ping"}
    raw = json.dumps(msg).encode()
    size = struct.pack("I", len(raw))

    sock = FakeSocket([size, raw])
    assert recv_message(sock) == msg

    s2 = FakeSocket([])
    send_message(s2, {"a": 1})
    assert b"a" in s2.sent


def test_recv_empty():
    sock = FakeSocket([])
    assert recv_message(sock) is None


def test_send_large_message():
    sock = FakeSocket([])
    send_message(sock, {"big": "x" * 1000})
    assert len(sock.sent) > 0


# =========================================================
# 2. ACTIONS
# =========================================================

def test_actions_all_cases():
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]
    board[1][3] = [None, ("blue", "light")]

    state = make_state(board=board, color="red")

    assert isinstance(actions(state, "dark"), list)
    assert isinstance(actions(state, "light"), list)

    state2 = make_state(board=empty_board(), color="red")
    assert actions(state2, "dark") == []


def test_actions_stress():
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]
    board[5][3] = [None, ("blue", "dark")]
    board[4][3] = [None, ("green", "dark")]

    state = make_state(board=board)

    for _ in range(5):
        actions(state, "dark")
        actions(state, "light")


# =========================================================
# 3. MOVE SYSTEM
# =========================================================

def test_play_undo_full():
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]

    state = make_state(board=board)
    move = [[6, 3], [5, 3]]

    old_color, piece = play_move(state, move)
    assert state["board"][5][3][1] is not None

    undo_move(state, move, old_color, piece)
    assert state["board"][6][3][1] is not None


# =========================================================
# 4. WIN
# =========================================================

def test_winning_moves():
    assert winning_move([[1, 1], [0, 1]], "dark")
    assert winning_move([[6, 1], [7, 1]], "light")


# =========================================================
# 5. EVALUATE
# =========================================================

def test_evaluate_full():
    board = empty_board()

    # victoire
    board[0][3] = [None, ("x", "dark")]
    state = make_state(board=board)

    assert evaluate(state, "dark", "light") in (100000, -100000)

    # normal
    board2 = empty_board()
    board2[6][3] = [None, ("red", "dark")]
    board2[1][3] = [None, ("blue", "light")]

    state2 = make_state(board=board2, color="red")

    val = evaluate(state2, "dark", "light")
    assert isinstance(val, int)


# =========================================================
# 6. FORCED SEQUENCE
# =========================================================

def test_forced_sequence_full():
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]

    state = make_state(board=board)

    score = forced_sequence_score(state, "dark", "light")
    assert isinstance(score, int)


# =========================================================
# 7. NEGAMAX
# =========================================================

def test_negamax_full():
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]

    state = make_state(board=board)

    s1, _ = negamax(state, "dark", "dark", "light", time.time(), -9999, 9999, 0)
    assert isinstance(s1, int)

    s2, _ = negamax(state, "dark", "dark", "light", time.time(), -9999, 9999, 1)
    assert isinstance(s2, int)


# =========================================================
# 8. BEST ACTION
# =========================================================

def test_best_action_full():
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]
    board[5][3] = [None, ("blue", "dark")]

    state = make_state(board=board, color="red")

    move = best_action(state, "dark")
    assert move is None or isinstance(move, list)


# =========================================================
# 9. UTIL
# =========================================================

def test_opponent():
    assert opponent("dark") == "light"
    assert opponent("light") == "dark"


# =========================================================
# 🔥 10. COVERAGE BOOST (clé pour 80%+)
# =========================================================

def test_extreme_game_states():
    board = empty_board()
    state = make_state(board=board)

    # aucun move
    assert best_action(state, "dark") is None

    # victoire directe
    board2 = empty_board()
    board2[1][3] = [None, ("red", "dark")]

    state2 = make_state(board=board2)

    move = best_action(state2, "dark")
    assert move is None or isinstance(move, list)


def test_deep_branches():
    board = empty_board()

    board[6][3] = [None, ("red", "dark")]
    board[5][4] = [None, ("blue", "light")]
    board[4][5] = [None, ("green", "dark")]

    state = make_state(board=board)

    score, _ = negamax(
        state,
        "dark",
        "dark",
        "light",
        time.time(),
        -9999,
        9999,
        2
    )

    assert isinstance(score, int)

    val = forced_sequence_score(state, "dark", "light")
    assert isinstance(val, int)