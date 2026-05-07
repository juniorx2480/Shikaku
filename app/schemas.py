from typing import Optional, List, Any
from sqlmodel import SQLModel


class PuzzleCreate(SQLModel):
    """Crea un puzzle Shikaku nuevo"""
    title: str
    description: Optional[str] = None
    rows: int
    cols: int
    grid: List[List[int]]  # Grilla 2D con numeros
    difficulty: Optional[str] = "medium"


class PuzzleRead(SQLModel):
    """Lee un puzzle Shikaku"""
    id: int
    title: str
    description: Optional[str]
    rows: int
    cols: int
    grid: List[List[int]]
    difficulty: Optional[str]
    created_at: str


class SolutionCreate(SQLModel):
    """Crea solucion (uso interno)"""
    puzzle_id: int
    rectangles: List[Any]
    solving_time_ms: Optional[float] = None


class SolutionRead(SQLModel):
    """Lee una solucion"""
    id: int
    puzzle_id: int
    rectangles: List[Any]
    solved_at: str
    solving_time_ms: Optional[float]


class SolveRequest(SQLModel):
    """Solicitud para resolver un puzzle"""
    grid: List[List[int]]


class SolveResponse(SQLModel):
    """Respuesta con solucion"""
    solved: bool
    rectangles: Optional[List[Any]] = None
    solving_time_ms: Optional[float] = None
    error: Optional[str] = None
