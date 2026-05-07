from typing import Optional, Any
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON


class Puzzle(SQLModel, table=True):
    """Puzzle Shikaku con grilla numerada"""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = None
    description: Optional[str] = None
    rows: int
    cols: int
    # Guarda la grilla en JSON: lista de listas con numeros
    grid: Any = Field(sa_column=Column(JSON))
    difficulty: Optional[str] = None  # easy, medium, hard
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Solution(SQLModel, table=True):
    """Solucion de un puzzle Shikaku"""
    id: Optional[int] = Field(default=None, primary_key=True)
    puzzle_id: int = Field(foreign_key="puzzle.id")
    # Guarda rectangulos como arreglo JSON
    rectangles: Any = Field(sa_column=Column(JSON))
    solved_at: datetime = Field(default_factory=datetime.utcnow)
    solving_time_ms: Optional[float] = None  # Tiempo usado para resolver
