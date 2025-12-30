from fastapi import FastAPI, HTTPException
from .chess_client import fetch_recent_games
from .ingestion import ingest_games
from .models import SessionLocal, Game
from sqlalchemy import func

app = FastAPI(title="ChessAnalytics Backend")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/games/{username}")
async def import_games_endpoint(username: str, limit: int = 100, mock: bool = True):
    try:
        games = await fetch_recent_games(username, limit, mock)
        return {"username": username, "games": games}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
