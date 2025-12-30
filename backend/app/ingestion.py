import chess
import chess.pgn
from io import StringIO
from .models import SessionLocal, User, Game
from typing import List, Dict, Any
import datetime

def get_opening_id(pgn_str: str) -> int:
    try:
        pgn = chess.pgn.read_game(StringIO(pgn_str))
        if pgn:
            board = pgn.board()
            moves = list(pgn.mainline_moves())
            if len(moves) >= 2:
                board.push(moves[0])
                board.push(moves[1])
                return "A00"
    except:
        pass
    return "Unknown"

def compute_elo_change(rating:int, opponent_rating: int, result: str) -> float:
    expected = 1 / (1 + 10 ** ((opponent_rating - rating) / 400))
    actual = 1 if result == 'win' else 0.5 if result == 'draw' else 0
    k = 32
    return k * (actual - expected)

def ingest_games(username: str, games: List[Dict[str, Any]]) -> None:
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username)
            session.add(user)
            session.commit()

        print("Flag 1.5")
        for game_data in games:
            existing = session.query(Game).filter_by(url=game_data['url']).first()
            if existing:
                continue

            result = game_data.get('result', 'unknown')
            if result == 'White':
                result_white = 'win'
                result_black = 'loss'
            elif result == 'Black':
                result_white = 'loss'
                result_black = 'win'
            else:
                result_white = 'draw'
                result_black = 'draw'
            
            white_rating = game_data['white'].get('rating', 1500)
            black_rating = game_data['black'].get('rating', 1500)
            elo_change_white = compute_elo_change(white_rating, black_rating, result_white)
            elo_change_black = compute_elo_change(black_rating, white_rating, result_black)

            opening_id = get_opening_id(game_data.get('pgn', ''))

            game = Game(
                url=game_data['url'],
                white_username=game_data['white']['username'],
                black_username=game_data['black']['username'],
                white_rating=white_rating,
                black_rating=black_rating,
                time_control=game_data.get('time_control'),
                time_class = game_data.get('time_class'),
                end_time=datetime.datetime.fromtimestamp(game_data['end_time']),
                pgn=game_data.get('pgn'),
                result=result,
                opening_id=opening_id,
                elo_change_white=elo_change_white,
                elo_change_black=elo_change_black,
                user_id=user.id
            )
            session.add(game)

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()