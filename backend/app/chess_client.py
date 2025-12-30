import httpx
import os
import json
from typing import List, Any

API_ARCHIVES = "https://api.chess.com/pub/player/{username}/games/archives"

async def fetch_archives(username: str):
    url = API_ARCHIVES.format(username=username)
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json().get("archives",[])
    
async def fetch_games_from_archive(archive_url: str):
    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.get(archive_url)
        response.raise_for_status()
        return response.json().get("games",[])
    
def load_mock_games(limit: int = 100) -> List[Any]:
    base = os.path.dirname(__file__)
    path = os.path.join(base, "mock_games.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data[:limit]
    except Exception:
        return []
    
async def fetch_recent_games(username: str, limit: int=100, use_mock: bool = False):
    if use_mock or os.environ.get("CHESS_API_MODE") == "mock":
        return load_mock_games(limit)
    
    archives = await fetch_archives(username)
    archives = sorted(archives, reverse=True)
    games = []
    for archive in archives:
        if len(games) >= limit:
            break
        try:
            gs = await fetch_games_from_archive(archive)
            games.extend(gs)
        except Exception:
            continue
    return games[:limit]
