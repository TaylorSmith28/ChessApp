import chess
import chess.pgn
from io import StringIO
from collections import Counter
import chess.svg
from chessdotcom import ChessDotComClient
from collections import defaultdict
import re
from IPython.display import SVG, display
import webbrowser
import os
from chess_display_board import show_fen_pygame

position_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0})

def sanitize_pgn_moves(pgn):
    """
    Convert a PGN string into a plain space-separated move list.
    Removes headers, comments, move numbers, ellipses, and game results.
    """
    # Remove PGN headers: lines starting with [
    pgn = re.sub(r"^\[.*?\]$", "", pgn, flags=re.MULTILINE)
    
    # Remove comments {...}
    pgn = re.sub(r"\{.*?\}", "", pgn)
    
    # Remove move numbers like 1. or 1...
    pgn = re.sub(r"\d+\.+\s*", "", pgn)
    
    # Remove game results (1-0, 0-1, 1/2-1/2)
    pgn = re.sub(r"(1-0|0-1|1/2-1/2)", "", pgn)
    
    # Normalize whitespace
    pgn = re.sub(r"\s+", " ", pgn).strip()
    
    return pgn

def normalized_fen(board):
    """
    Returns a normalized FEN that ignores:
    - move counters
    - en passant
    """
    return f"{board.board_fen()} {board.turn}"

def extract_positions_from_pgn(pgn_text):
    game = chess.pgn.read_game(StringIO(pgn_text))
    board = game.board()

    positions = []

    for move in game.mainline_moves():
        board.push(move)
        positions.append(normalized_fen(board))

    return positions

def collect_common_positions(pgn_list):
    """
    pgn_list: list of PGN strings (all assumed losses)
    """
    position_counter = Counter()

    for pgn_text in pgn_list:
        positions = extract_positions_from_pgn(pgn_text)
        position_counter.update(positions)

    return position_counter

def most_common_positions(position_counter, min_occurrences=3, top_n=10):
    return [
        (fen, count)
        for fen, count in position_counter.most_common(top_n)
        if count >= min_occurrences
    ]

def save_position_svg(fen, filename):
    board = chess.Board(fen.split()[0] + " w - - 0 1")
    svg = chess.svg.board(board)
    with open(filename, "w") as f:
        f.write(svg)

def show_fen(normalized_fen):
    board_fen, turn = normalized_fen.split()

    # Convert boolean to 'w' / 'b'
    turn_char = 'w' if turn == 'True' else 'b'

    # Construct full valid FEN
    full_fen = f"{board_fen} {turn_char} - - 0 1"

    board = chess.Board(full_fen)
    display(SVG(chess.svg.board(board)))

def fix_fen(fen):
    parts = fen.split()
    
    # Only board layout present
    if len(parts) == 1:
        return parts[0] + " w - - 0 1"

    # Board + boolean turn
    if parts[-1] in ("True", "False"):
        turn = "w" if parts[-1] == "True" else "b"
        return parts[0] + f" {turn} - - 0 1"

    return fen

def filter_positions(positions_counter, min_depth=5, min_count=3):
    """
    Filter positions by:
        - min_depth: minimum ply (half-moves) from the start
        - min_count: minimum number of times this position occurs
    Returns a dict of filtered FENs with counts.
    """
    filtered = {}
    for fen, count in positions_counter.items():
        fen = fix_fen(fen)
        board = chess.Board(fen)
        depth = board.fullmove_number * 2
        if not board.turn:  # if black to move, add 1 for half-move
            depth += 1
        if depth >= min_depth and count >= min_count:
            filtered[fen] = count
    return filtered


client = ChessDotComClient(user_agent = "My Python Application...")

response = client.get_player_profile("TheWaywardHippo")

response = client.get_player_games_by_month("TheWaywardHippo",2025,10).json

print(response['games'][0].keys())

x = 0
ratings = []
loss_openings = []
win_openings = []
pgns = []
while x < len(response['games']):
    if response['games'][x]['white']['username'] == 'TheWaywardHippo':
        ratings.append(response['games'][x]['white']['rating'])
        if response['games'][x]['white']['result'] != 'win':
            pgns.append(sanitize_pgn_moves(response['games'][x]['pgn']))
    else:
        ratings.append(response['games'][x]['black']['rating'])
        if response['games'][x]['black']['result'] != 'win':
            pgns.append(sanitize_pgn_moves(response['games'][x]['pgn']))
    

    x+=1

position_counter = collect_common_positions(pgns)

filtered_positions = filter_positions(position_counter, min_depth=3, min_count=20)

# Visualize the first position
for fen, count in filtered_positions.items():
    print(f"Seen {count} times, depth: {chess.Board(fen).fullmove_number} -> {fen}")
    show_fen_pygame(fen)  # your pygame function
