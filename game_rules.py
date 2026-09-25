"""Shared, side-effect-free tic-tac-toe rules."""

WINNING_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def legal_moves(state):
    return [str(i) for i, cell in enumerate(state) if cell not in ("X", "O")]


def winner(state):
    for a, b, c in WINNING_LINES:
        if state[a] in ("X", "O") and state[a] == state[b] == state[c]:
            return state[a]
    return None if legal_moves(state) else "Draw"


def tactical_move(state, turn):
    """Take an immediate win before considering any blocking move."""
    for symbol in (turn, "O" if turn == "X" else "X"):
        for move in legal_moves(state):
            candidate = list(state)
            candidate[int(move)] = symbol
            if winner(candidate) == symbol:
                return True, move
    return False, "0"


def board_position(x, y):
    """Return a cell only for clicks inside the 300 by 300 game board."""
    if not (0 <= x < 300 and 0 <= y < 300):
        return None
    row, col = y // 100, x // 100
    return str(row * 3 + col), row, col
