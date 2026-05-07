"""
Shikaku Solver API - Backend FastAPI

Endpoints principales:
- POST   /api/puzzles            - Crear puzzle nuevo
- GET    /api/puzzles            - Listar puzzles
- GET    /api/puzzles/{id}       - Obtener puzzle por id
- DELETE /api/puzzles/{id}       - Eliminar puzzle
- POST   /api/puzzles/{id}/solve - Resolver puzzle guardado
"""

import time
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from . import models
from .database import init_db, get_session
from .schemas import (
    PuzzleCreate, PuzzleRead, SolveRequest, SolveResponse, 
    SolutionCreate, SolutionRead
)
from .shikaku_solver import solve_shikaku


app = FastAPI(
    title="Shikaku Solver API",
    description="API for solving Shikaku puzzles using backtracking algorithm",
    version="1.0.0"
)

# Activa CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Inicia base de datos al arrancar"""
    init_db()


# ========================
# Salud de API
# ========================

@app.get("/", tags=["Health"])
def root():
    """Verifica estado basico de API"""
    return {
        "status": "ok",
        "message": "Shikaku Solver API is running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
def health():
    """Verifica estado detallado de API"""
    return {
        "status": "healthy",
        "service": "Shikaku Solver",
        "database": "connected"
    }


# ========================
# Gestion de puzzles
# ========================

@app.post("/api/puzzles", response_model=PuzzleRead, tags=["Puzzles"])
def create_puzzle(
    puzzle: PuzzleCreate,
    session: Session = Depends(get_session)
):
    """Crea un puzzle Shikaku nuevo"""
    if puzzle.rows <= 0 or puzzle.cols <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rows and cols must be positive"
        )
    
    if len(puzzle.grid) != puzzle.rows or any(len(row) != puzzle.cols for row in puzzle.grid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grid dimensions don't match rows/cols"
        )
    
    db_puzzle = models.Puzzle(
        title=puzzle.title,
        description=puzzle.description,
        rows=puzzle.rows,
        cols=puzzle.cols,
        grid=puzzle.grid,
        difficulty=puzzle.difficulty
    )
    session.add(db_puzzle)
    session.commit()
    session.refresh(db_puzzle)
    
    return PuzzleRead(
        id=db_puzzle.id,
        title=db_puzzle.title,
        description=db_puzzle.description,
        rows=db_puzzle.rows,
        cols=db_puzzle.cols,
        grid=db_puzzle.grid,
        difficulty=db_puzzle.difficulty,
        created_at=db_puzzle.created_at.isoformat()
    )


@app.get("/api/puzzles", response_model=list[PuzzleRead], tags=["Puzzles"])
def list_puzzles(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Lista puzzles con paginacion"""
    statement = select(models.Puzzle).offset(skip).limit(limit)
    puzzles = session.exec(statement).all()
    
    return [
        PuzzleRead(
            id=p.id,
            title=p.title,
            description=p.description,
            rows=p.rows,
            cols=p.cols,
            grid=p.grid,
            difficulty=p.difficulty,
            created_at=p.created_at.isoformat()
        )
        for p in puzzles
    ]


@app.get("/api/puzzles/{puzzle_id}", response_model=PuzzleRead, tags=["Puzzles"])
def get_puzzle(
    puzzle_id: int,
    session: Session = Depends(get_session)
):
    """Obtiene un puzzle por id"""
    statement = select(models.Puzzle).where(models.Puzzle.id == puzzle_id)
    puzzle = session.exec(statement).first()
    
    if not puzzle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puzzle not found"
        )
    
    return PuzzleRead(
        id=puzzle.id,
        title=puzzle.title,
        description=puzzle.description,
        rows=puzzle.rows,
        cols=puzzle.cols,
        grid=puzzle.grid,
        difficulty=puzzle.difficulty,
        created_at=puzzle.created_at.isoformat()
    )


@app.delete("/api/puzzles/{puzzle_id}", tags=["Puzzles"])
def delete_puzzle(
    puzzle_id: int,
    session: Session = Depends(get_session)
):
    """Elimina un puzzle por id"""
    statement = select(models.Puzzle).where(models.Puzzle.id == puzzle_id)
    puzzle = session.exec(statement).first()
    
    if not puzzle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puzzle not found"
        )
    
    session.delete(puzzle)
    session.commit()
    
    return {"message": "Puzzle deleted successfully"}


# ========================
# Solver - endpoint principal
# ========================

@app.post("/api/solve", response_model=SolveResponse, tags=["Solver"])
def solve_puzzle_direct(
    request: SolveRequest,
    session: Session = Depends(get_session)
):
    """
    Resuelve un puzzle Shikaku directo sin guardar

    Algoritmo: backtracking con poda
    - Complejidad tiempo: O(n·m²) promedio
    - Complejidad espacio: O(n·m)
    """
    try:
        # Valida grilla
        if not request.grid or len(request.grid) == 0:
            raise ValueError("Grid cannot be empty")
        
        cols = len(request.grid[0])
        if not all(len(row) == cols for row in request.grid):
            raise ValueError("All rows must have the same number of columns")
        
        # Mide tiempo de resolucion
        start_time = time.time()
        solution = solve_shikaku(request.grid)
        elapsed_time = (time.time() - start_time) * 1000  # Convierte a milisegundos
        
        if solution:
            return SolveResponse(
                solved=True,
                rectangles=solution,
                solving_time_ms=round(elapsed_time, 2)
            )
        else:
            return SolveResponse(
                solved=False,
                error="No solution found for this puzzle"
            )
    
    except ValueError as e:
        return SolveResponse(
            solved=False,
            error=str(e)
        )
    except Exception as e:
        return SolveResponse(
            solved=False,
            error=f"Solver error: {str(e)}"
        )


@app.post("/api/puzzles/{puzzle_id}/solve", response_model=SolveResponse, tags=["Solver"])
def solve_stored_puzzle(
    puzzle_id: int,
    session: Session = Depends(get_session)
):
    """Resuelve un puzzle guardado y guarda la solucion"""
    # Obtiene puzzle
    statement = select(models.Puzzle).where(models.Puzzle.id == puzzle_id)
    puzzle = session.exec(statement).first()
    
    if not puzzle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puzzle not found"
        )
    
    # Resuelve
    start_time = time.time()
    solution = solve_shikaku(puzzle.grid)
    elapsed_time = (time.time() - start_time) * 1000
    
    if not solution:
        return SolveResponse(
            solved=False,
            error="No solution found for this puzzle"
        )
    
    # Guarda solucion en base de datos
    db_solution = models.Solution(
        puzzle_id=puzzle.id,
        rectangles=solution,
        solving_time_ms=elapsed_time
    )
    session.add(db_solution)
    session.commit()
    session.refresh(db_solution)
    
    return SolveResponse(
        solved=True,
        rectangles=solution,
        solving_time_ms=round(elapsed_time, 2)
    )


@app.get("/api/puzzles/{puzzle_id}/solutions", response_model=list[SolutionRead], tags=["Solutions"])
def get_puzzle_solutions(
    puzzle_id: int,
    session: Session = Depends(get_session)
):
    """Obtiene todas las soluciones de un puzzle"""
    # Verifica que el puzzle exista
    statement = select(models.Puzzle).where(models.Puzzle.id == puzzle_id)
    puzzle = session.exec(statement).first()
    
    if not puzzle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puzzle not found"
        )
    
    # Obtiene soluciones
    statement = select(models.Solution).where(models.Solution.puzzle_id == puzzle_id)
    solutions = session.exec(statement).all()
    
    return [
        SolutionRead(
            id=s.id,
            puzzle_id=s.puzzle_id,
            rectangles=s.rectangles,
            solved_at=s.solved_at.isoformat(),
            solving_time_ms=s.solving_time_ms
        )
        for s in solutions
    ]


# ========================
# Info y estadisticas
# ========================

@app.get("/api/stats", tags=["Stats"])
def get_statistics(session: Session = Depends(get_session)):
    """Obtiene estadisticas de API"""
    total_puzzles = session.exec(select(models.Puzzle)).all().__len__()
    total_solutions = session.exec(select(models.Solution)).all().__len__()
    
    return {
        "total_puzzles": total_puzzles,
        "total_solutions": total_solutions,
        "algorithm": "Backtracking with Constraint Propagation",
        "time_complexity": "O(n·m²) average case",
        "space_complexity": "O(n·m)"
    }


@app.get("/api/algorithm-info", tags=["Info"])
def algorithm_info():
    """Obtiene informacion del algoritmo de resolucion"""
    return {
        "name": "Backtracking with Optimizations",
        "description": "Solves Shikaku puzzles by recursive placement of rectangles",
        "steps": [
            "1. Extract numbered cells from grid",
            "2. For each numbered cell, calculate possible rectangle dimensions",
            "3. Try placing rectangle, recursively solve rest",
            "4. If conflict, backtrack and try next rectangle",
            "5. Continue until all cells covered or no solution"
        ],
        "optimizations": [
            "Precompute valid rectangles per cell",
            "Filter rectangles containing multiple numbers",
            "Early conflict detection",
            "Top-left ordering heuristic",
            "Cell occupancy tracking"
        ],
        "time_complexity": "O(n·m²) average, exponential worst case",
        "space_complexity": "O(n·m) for occupied cells grid",
        "problem_class": "NP-Complete (backtracking exhaustive search)"
    }
