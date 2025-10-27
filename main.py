from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional, Tuple

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Game Logic ---
WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

def check_winner(b: List[str]) -> Optional[str]:
    for a, c, d in WIN_LINES:
        if b[a] != ' ' and b[a] == b[c] == b[d]:
            return b[a]
    return None

def board_full(b: List[str]) -> bool:
    return all(cell != ' ' for cell in b)

def available_moves(b: List[str]) -> List[int]:
    return [i for i, cell in enumerate(b) if cell == ' ']

def minimax(b: List[str], player: str) -> Tuple[int, Optional[int]]:
    winner = check_winner(b)
    if winner == 'X': return 1, None
    if winner == 'O': return -1, None
    if board_full(b): return 0, None

    if player == 'X':
        best, move = -999, None
        for i in available_moves(b):
            b[i] = 'X'
            score, _ = minimax(b, 'O')
            b[i] = ' '
            if score > best: best, move = score, i
        return best, move
    else:
        best, move = 999, None
        for i in available_moves(b):
            b[i] = 'O'
            score, _ = minimax(b, 'X')
            b[i] = ' '
            if score < best: best, move = score, i
        return best, move

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/cpu_move")
async def cpu_move(data: dict):
    board = data["board"]
    cpu_mark = data["cpu"]
    _, move = minimax(board, cpu_mark)
    return JSONResponse({"move": move})

@app.post("/check")
async def check(data: dict):
    board = data["board"]
    winner = check_winner(board)
    tie = board_full(board) and not winner
    return JSONResponse({"winner": winner, "tie": tie})
