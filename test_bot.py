import json
import struct
import time
import random

import bot as b

b.MON_NOM = "Thomas "
b.TEMPS_MAX = 2.8


class FakeSocket:
    def __init__(self, chunks=None):
        self.chunks = list(chunks) if chunks else []
        self.sent = b""

    def recv(self, n):
        return self.chunks.pop(0) if self.chunks else b""

    def sendall(self, data):
        self.sent += data

    def connect(self, addr): pass
    def bind(self, addr): pass
    def listen(self): pass

    def accept(self):
        msg = json.dumps({"request": "ping"}).encode()
        packet = struct.pack("I", len(msg)) + msg
        return FakeSocket([packet]), None


def empty_board():
    return [[[None, None] for _ in range(8)] for _ in range(8)]


def full_state(color=None):
    return {
        "board": empty_board(),
        "players": ["Thomas ", "Bot"],
        "color": color,
        "current": 0,
    }


def board_with_piece(i, j, color, kind):
    board = empty_board()
    board[i][j] = [None, (color, kind)]
    return board


def board_many_pieces():
    board = empty_board()
    for i in range(8):
        for j in range(8):
            if (i + j) % 3 == 0:
                board[i][j] = [None, ("red", "dark")]
            elif (i + j) % 3 == 1:
                board[i][j] = [None, ("blue", "light")]
    return board


def test_recv_basic():
    msg = json.dumps({"a": 1}).encode()
    sock = FakeSocket([struct.pack("I", len(msg)), msg])
    assert b.recv_message(sock) == {"a": 1}


def test_recv_empty():
    assert b.recv_message(FakeSocket([])) is None


def test_recv_split_chunks():
    msg = json.dumps({"x": 1}).encode()
    sock = FakeSocket([struct.pack("I", len(msg)), msg[:2], msg[2:]])
    assert b.recv_message(sock) == {"x": 1}


def test_recv_many_packets():
    msg = json.dumps({"multi": True}).encode()
    sock = FakeSocket([struct.pack("I", len(msg)), msg[:1], msg[1:5], msg[5:]])
    assert b.recv_message(sock) == {"multi": True}


def test_send():
    sock = FakeSocket()
    b.send_message(sock, {"test": 123})
    assert b"test" in sock.sent


def test_fake_server_ping():
    msg = json.dumps({"request": "ping"}).encode()
    sock = FakeSocket([struct.pack("I", len(msg)), msg])
    result = b.recv_message(sock)
    assert result["request"] == "ping"


def test_opponent_dark():
    assert b.opponent("dark") == "light"


def test_opponent_light():
    assert b.opponent("light") == "dark"


def test_my_kind_dark():
    state = full_state()
    assert b.my_kind(state) == "dark"


def test_my_kind_light():
    state = {
        "board": empty_board(),
        "players": ["Bot", "Thomas "],
        "color": None,
        "current": 0,
    }
    assert b.my_kind(state) == "light"


def test_score_move_winning_dark():
    move = [[1, 3], [0, 3]]
    assert b.score_move(move, "dark") == 10000


def test_score_move_winning_light():
    move = [[6, 3], [7, 3]]
    assert b.score_move(move, "light") == 10000


def test_score_move_dark_progress():
    move = [[6, 3], [5, 3]]
    assert b.score_move(move, "dark") > 0


def test_score_move_light_progress():
    move = [[1, 3], [2, 3]]
    assert b.score_move(move, "light") > 0


def test_sort_moves_dark():
    moves = [[[6, 3], [5, 3]], [[1, 3], [0, 3]], [[4, 4], [3, 4]]]
    sorted_moves = b.sort_moves(moves, "dark")
    assert sorted_moves[0] == [[1, 3], [0, 3]]


def test_sort_moves_light():
    moves = [[[1, 3], [2, 3]], [[6, 3], [7, 3]], [[4, 4], [5, 4]]]
    sorted_moves = b.sort_moves(moves, "light")
    assert sorted_moves[0] == [[6, 3], [7, 3]]


def test_actions_empty_board():
    state = full_state()
    assert b.actions(state, "dark") == []


def test_actions_dark_piece():
    state = full_state()
    state["board"] = board_with_piece(6, 3, "red", "dark")
    assert len(b.actions(state, "dark")) > 0


def test_actions_light_piece():
    state = full_state()
    state["board"] = board_with_piece(1, 3, "blue", "light")
    assert len(b.actions(state, "light")) > 0


def test_actions_wrong_kind():
    state = full_state()
    state["board"] = board_with_piece(6, 3, "red", "dark")
    assert b.actions(state, "light") == []


def test_actions_color_filter_match():
    state = full_state(color="red")
    state["board"] = board_with_piece(6, 3, "red", "dark")
    assert len(b.actions(state, "dark")) > 0


def test_actions_color_filter_no_match():
    state = full_state(color="red")
    state["board"] = board_with_piece(6, 3, "blue", "dark")
    assert b.actions(state, "dark") == []


def test_actions_blocked_by_piece():
    state = full_state()
    state["board"][6][3] = [None, ("red", "dark")]
    state["board"][5][3] = [None, ("blue", "light")]
    moves = b.actions(state, "dark")
    assert [5, 3] not in [m[1] for m in moves]


def test_actions_full_board():
    state = full_state()
    state["board"] = board_many_pieces()
    b.actions(state, "dark")
    b.actions(state, "light")


def test_actions_diagonal():
    state = full_state()
    state["board"] = board_with_piece(4, 4, "red", "dark")
    moves = b.actions(state, "dark")
    assert any(m[1][0] < 4 for m in moves)


def test_play_and_undo():
    state = full_state()
    state["board"] = board_with_piece(6, 3, "red", "dark")
    move = [[6, 3], [5, 3]]
    old, piece = b.play_move(state, move)
    assert state["board"][6][3][1] is None
    assert state["board"][5][3][1] == piece
    b.undo_move(state, move, old, piece)
    assert state["board"][6][3][1] == piece
    assert state["board"][5][3][1] is None


def test_play_updates_color():
    state = full_state()
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]
    board[5][3] = ["green", None]
    state["board"] = board
    old, piece = b.play_move(state, [[6, 3], [5, 3]])
    assert state["color"] == "green"
    b.undo_move(state, [[6, 3], [5, 3]], old, piece)
    assert state["color"] is None


def test_play_undo_multiple():
    state = full_state()
    state["board"] = board_with_piece(6, 3, "red", "dark")
    for _ in range(10):
        move = [[6, 3], [5, 3]]
        old, piece = b.play_move(state, move)
        b.undo_move(state, move, old, piece)


def test_winning_dark_row0():
    assert b.winning_move([[1, 1], [0, 1]], "dark")


def test_winning_light_row7():
    assert b.winning_move([[6, 1], [7, 1]], "light")


def test_no_win_middle():
    assert not b.winning_move([[3, 3], [3, 4]], "dark")
    assert not b.winning_move([[3, 3], [4, 4]], "light")


def test_dark_not_win_row7():
    assert not b.winning_move([[6, 3], [7, 3]], "dark")


def test_light_not_win_row0():
    assert not b.winning_move([[1, 3], [0, 3]], "light")


def test_evaluate_empty():
    state = full_state()
    assert isinstance(b.evaluate(state, "dark", "light"), (int, float))


def test_evaluate_dark_wins():
    state = full_state()
    state["board"][0][3] = [None, ("x", "dark")]
    assert b.evaluate(state, "dark", "light") == 100000


def test_evaluate_dark_wins_seen_as_opp():
    state = full_state()
    state["board"][0][3] = [None, ("x", "dark")]
    assert b.evaluate(state, "light", "dark") == -100000


def test_evaluate_light_wins():
    state = full_state()
    state["board"][7][3] = [None, ("x", "light")]
    assert b.evaluate(state, "light", "dark") == 100000


def test_evaluate_light_wins_seen_as_opp():
    state = full_state()
    state["board"][7][3] = [None, ("x", "light")]
    assert b.evaluate(state, "dark", "light") == -100000


def test_evaluate_progress():
    state = full_state()
    state["board"] = board_with_piece(6, 3, "red", "dark")
    b.evaluate(state, "dark", "light")


def test_evaluate_mobility():
    state = full_state()
    state["board"] = board_many_pieces()
    b.evaluate(state, "dark", "light")


def test_evaluate_color_opp_zero_moves():
    state = full_state(color="red")
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]
    state["board"] = board
    assert b.evaluate(state, "dark", "light") > 0


def test_evaluate_opp_winning_color_move():
    state = full_state(color="blue")
    board = empty_board()
    board[6][3] = [None, ("blue", "light")]
    board[7][3] = ["blue", None]
    state["board"] = board
    assert b.evaluate(state, "dark", "light") < 0


def test_evaluate_me_winning_color_move():
    state = full_state(color="red")
    board = empty_board()
    board[1][3] = [None, ("red", "dark")]
    board[0][3] = ["red", None]
    state["board"] = board
    assert b.evaluate(state, "dark", "light") > 0


def test_evaluate_low_opp_mobility():
    state = full_state()
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]
    state["board"] = board
    b.evaluate(state, "dark", "light")


def test_forced_empty():
    assert b.forced_sequence_score(full_state(), "dark", "light") == 0


def test_forced_basic():
    state = full_state()
    state["board"] = board_with_piece(6, 3, "red", "dark")
    b.forced_sequence_score(state, "dark", "light")


def test_forced_many_pieces():
    state = full_state()
    state["board"] = board_many_pieces()
    b.forced_sequence_score(state, "dark", "light")


def test_forced_opp_no_moves():
    state = full_state()
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]
    state["board"] = board
    assert b.forced_sequence_score(state, "dark", "light") == 10000


def test_forced_opp_one_move_then_win():
    state = full_state()
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]
    board[2][3] = [None, ("blue", "light")]
    board[1][3] = [None, ("red", "dark")]
    state["board"] = board
    assert isinstance(b.forced_sequence_score(state, "dark", "light"), (int, float))


def test_forced_opp_one_move_score_200():
    state = full_state()
    board = empty_board()
    board[6][3] = [None, ("red", "dark")]
    board[2][4] = [None, ("blue", "light")]
    state["board"] = board
    assert isinstance(b.forced_sequence_score(state, "dark", "light"), (int, float))


def test_negamax_depth0():
    state = full_state()
    score, timeout = b.negamax(state, "dark", "dark", "light", time.time(), -9999, 9999, 0)
    assert isinstance(score, (int, float))
    assert not timeout


def test_negamax_depth1():
    state = full_state()
    state["board"] = board_with_piece(6, 3, "red", "dark")
    score, timeout = b.negamax(state, "dark", "dark", "light", time.time(), -9999, 9999, 1)
    assert isinstance(score, (int, float))


def test_negamax_depth2():
    state = full_state()
    state["board"] = board_many_pieces()
    b.negamax(state, "dark", "dark", "light", time.time(), -9999, 9999, 2)


def test_negamax_timeout():
    state = full_state()
    _, timeout = b.negamax(state, "dark", "dark", "light", time.time() - 10, -9999, 9999, 3)
    assert timeout


def test_negamax_no_moves():
    state = full_state()
    score, _ = b.negamax(state, "dark", "dark", "light", time.time(), -9999, 9999, 3)
    assert isinstance(score, (int, float))


def test_negamax_winning_move_found():
    state = full_state()
    state["board"] = board_with_piece(1, 3, "red", "dark")
    score, _ = b.negamax(state, "dark", "dark", "light", time.time(), -9999, 9999, 2)
    assert score == 100000


def test_negamax_alpha_beta_pruning():
    state = full_state()
    state["board"] = board_many_pieces()
    b.negamax(state, "dark", "dark", "light", time.time(), 9999, -9999, 2)


def test_best_action_empty():
    assert b.best_action(full_state(), "dark") is None


def test_best_action_normal():
    state = full_state()
    state["board"] = board_with_piece(6, 3, "red", "dark")
    assert b.best_action(state, "dark") is not None


def test_best_action_immediate_win():
    state = full_state()
    state["board"] = board_with_piece(1, 3, "red", "dark")
    move = b.best_action(state, "dark")
    assert move is not None
    assert b.winning_move(move, "dark")


def test_best_action_light_wins():
    state = full_state()
    state["board"] = board_with_piece(6, 3, "red", "light")
    move = b.best_action(state, "light")
    assert move is not None
    assert b.winning_move(move, "light")


def test_best_action_many_moves():
    state = full_state()
    state["board"] = board_many_pieces()
    assert b.best_action(state, "dark") is not None


def test_best_action_timeout():
    original = b.TEMPS_MAX
    b.TEMPS_MAX = 0.0
    state = full_state()
    state["board"] = board_many_pieces()
    b.best_action(state, "dark")
    b.TEMPS_MAX = original


def test_stress_all_functions():
    state = full_state()
    state["board"] = board_many_pieces()
    for _ in range(30):
        b.actions(state, "dark")
        b.actions(state, "light")
        b.evaluate(state, "dark", "light")
        b.evaluate(state, "light", "dark")
        b.forced_sequence_score(state, "dark", "light")
        b.negamax(state, "dark", "dark", "light", time.time(), -500, 500, 1)


def test_fuzz_random_states():
    colors = ["red", "blue", "green", None]
    for _ in range(50):
        state = full_state(color=random.choice(colors))
        board = empty_board()
        for _ in range(10):
            i, j = random.randint(0, 7), random.randint(0, 7)
            board[i][j] = [None, (random.choice(["red", "blue"]), random.choice(["dark", "light"]))]
        state["board"] = board
        try:
            b.actions(state, "dark")
            b.evaluate(state, "dark", "light")
            b.forced_sequence_score(state, "dark", "light")
            b.best_action(state, "dark")
        except Exception:
            pass