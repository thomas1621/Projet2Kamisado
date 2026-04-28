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


