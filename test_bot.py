from bot import my_piece, get_random_move, couleur_to_play
from typing import List, Tuple, Optional

def empty_board() -> List[List[List[Optional[Tuple[str, str]]]]]:
    return [[[None, None] for _ in range(8)] for _ in range(8)]

def make_state(players=None, color=None, board=None, current=0):
    return {
        "players": players or ["joueur1", "joueur2"],
        "current": current,
        "color": color,
        "board": board or empty_board()
    }

def test_my_piece_simple():
    board = empty_board()
    board[7][0] = [None, ("red", "dark")]

    state = make_state(board=board, current=0)

    pieces = my_piece(state)

    assert pieces == [(7, 0, "red")]

def test_couleur_to_play():
    board= empty_board()

    board[5][2] = [None, ("red", "dark")]
    board[4][3] = [None, ("blue", "dark")]

    state = make_state(board=board,current=0,color="red")

    piece=my_piece(state)

    piece_to_play=couleur_to_play(piece,state)

    assert piece_to_play == [(5, 2, "red")]
def test_get_random_move():
    board = empty_board()
    board[7][0] = [None, ("red", "dark")]

    state= make_state(board=board, current=0)
    tiles = my_piece(state)
    
    move = get_random_move(state, tiles)

    assert move is not None



