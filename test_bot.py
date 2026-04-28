from bot import my_piece, get_random_move, couleur_to_play


# ---------- OUTILS ----------

def empty_board() -> list[list[list[tuple[str, str] | None]]]:
    return [[[None, None] for _ in range(8)] for _ in range(8)]

def make_state(players=None, color=None, board=None, current=0):
    return {
        "players": players or ["joueur1", "joueur2"],
        "current": current,
        "color": color,
        "board": board or empty_board()
    }


# ---------- TESTS my_piece ----------

def test_my_piece_simple():
    board = empty_board()
    board[7][0] = [None, ("red", "dark")]

    state = make_state(board=board, current=0)

    pieces = my_piece(state)

    assert pieces == [(7, 0, "red")]


def test_my_piece_multiple():
    board = empty_board()
    board[7][0] = [None, ("red", "dark")]
    board[6][1] = [None, ("blue", "dark")]
    board[0][0] = [None, ("green", "light")]  # adversaire

    state = make_state(board=board, current=0)

    pieces = my_piece(state)

    assert len(pieces) == 2


# ---------- TESTS couleur_to_play ----------

def test_couleur_to_play_none():
    tiles = [(0, 0, "red"), (1, 1, "blue")]

    state = make_state(color=None)

    result = couleur_to_play(tiles, state)

    assert result == tiles


def test_couleur_to_play_filter():
    tiles = [(0, 0, "red"), (1, 1, "blue")]

    state = make_state(color="red")

    result = couleur_to_play(tiles, state)

    assert result == [(0, 0, "red")]


# ---------- TESTS get_random_move ----------

def test_get_random_move_exists():
    board = empty_board()
    board[4][4] = [None, ("red", "dark")]

    state = make_state(board=board, current=0)
    tiles = [(4, 4, "red")]

    move = get_random_move(state, tiles)

    assert move is not None
    assert len(move) == 2


def test_get_random_move_blocked():
    board = empty_board()

    # pièce bloquée (devant occupé)
    board[4][4] = [None, ("red", "dark")]
    board[3][4] = [None, ("blue", "light")]

    state = make_state(board=board, current=0)
    tiles = [(4, 4, "red")]

    move = get_random_move(state, tiles)

    assert move is None


# ---------- TEST BUG IMPORTANT ----------

def test_no_tiles():
    state = make_state()

    tiles = []

    move = get_random_move(state, tiles)

    assert move is None