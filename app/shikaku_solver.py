"""
Shikaku Puzzle Solver - Implementacion de logica pura

Reglas de Shikaku:
1. Divide la grilla en rectangulos
2. Cada rectangulo contiene un solo numero
3. El area del rectangulo es igual al numero que contiene
"""

from typing import List, Tuple, Optional, Set, Dict
from dataclasses import dataclass


@dataclass
class Rectangle:
    """Representa un rectangulo en la solucion"""
    row: int
    col: int
    height: int
    width: int
    number: int  # Numero que contiene el rectangulo

    def get_cells(self) -> Set[Tuple[int, int]]:
        """Retorna todas las celdas (row, col) de este rectangulo"""
        cells = set()
        for r in range(self.row, self.row + self.height):
            for c in range(self.col, self.col + self.width):
                cells.add((r, c))
        return cells

    def area(self) -> int:
        """Retorna el area del rectangulo"""
        return self.height * self.width


class ShikakuSolver:
    """Solver para puzzles Shikaku usando backtracking"""

    def __init__(self, grid: List[List[int]]):
        """Inicializa el solver con la grilla del puzzle"""
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        
        # Valida dimensiones de grilla
        if not all(len(row) == self.cols for row in grid):
            raise ValueError("All rows must have the same number of columns")
        
        # Encuentra celdas numeradas
        self.numbered_cells: Dict[Tuple[int, int], int] = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if grid[r][c] > 0:
                    self.numbered_cells[(r, c)] = grid[r][c]

    def get_possible_rectangles(self, r: int, c: int, area: int) -> List[Rectangle]:
        """Obtiene todos los rectangulos posibles para celda y area dada"""
        possible = []
        
        # Prueba todos los divisores del area como alturas
        for height in range(1, area + 1):
            if area % height != 0:
                continue
            
            width = area // height
            
            # Prueba posiciones donde (r, c) cae dentro del rectangulo
            for top in range(max(0, r - height + 1), min(self.rows - height + 1, r + 1)):
                for left in range(max(0, c - width + 1), min(self.cols - width + 1, c + 1)):
                    rect = Rectangle(top, left, height, width, self.grid[r][c])
                    
                    # Verifica si el rectangulo contiene otra celda numerada
                    valid = True
                    for cell_r, cell_c in rect.get_cells():
                        if (cell_r, cell_c) in self.numbered_cells:
                            if (cell_r, cell_c) != (r, c):
                                valid = False
                                break
                    
                    if valid:
                        possible.append(rect)
        
        return possible

    def is_valid_assignment(
        self,
        assignment: List[Rectangle],
        occupied: Set[Tuple[int, int]]
    ) -> bool:
        """Verifica si la asignacion actual es valida sin solapes"""
        for rect in assignment:
            cells = rect.get_cells()
            if cells & occupied:
                return False
            occupied.update(cells)
        
        return True

    def solve(self) -> Optional[List[Rectangle]]:
        """Resuelve el puzzle Shikaku con backtracking"""
        # Ordena celdas numeradas por posicion (arriba a abajo, izquierda a derecha)
        numbered_list = sorted(self.numbered_cells.items(), key=lambda x: (x[0][0], x[0][1]))
        
        assignment: List[Rectangle] = []
        occupied: Set[Tuple[int, int]] = set()
        
        def backtrack(index: int) -> bool:
            """Funcion recursiva de backtracking"""
            # Caso base: todas las celdas numeradas ya tienen rectangulo
            if index == len(numbered_list):
                # Verifica si todas las celdas estan cubiertas
                if len(occupied) == self.rows * self.cols:
                    return True
                return False
            
            # Obtiene celda actual y numero
            (r, c), area = numbered_list[index]
            
            # Obtiene rectangulos posibles para la celda
            possible_rects = self.get_possible_rectangles(r, c, area)
            
            # Prueba cada rectangulo posible
            for rect in possible_rects:
                cells = rect.get_cells()
                
                # Verifica que todas las celdas esten libres
                if cells & occupied:
                    continue
                
                # Coloca rectangulo
                assignment.append(rect)
                occupied.update(cells)
                
                # Intenta resolver el resto
                if backtrack(index + 1):
                    return True
                
                # Revierte asignacion
                assignment.pop()
                occupied.difference_update(cells)
            
            return False
        
        # Ejecuta backtracking
        if backtrack(0):
            return assignment
        
        return None

    def solution_to_dict(self, solution: List[Rectangle]) -> List[Dict]:
        """Convierte la solucion a diccionario para serializacion"""
        return [
            {
                "row": rect.row,
                "col": rect.col,
                "height": rect.height,
                "width": rect.width,
                "number": rect.number,
                "cells": sorted(list(rect.get_cells()))
            }
            for rect in solution
        ]


def solve_shikaku(grid: List[List[int]]) -> Optional[List[Dict]]:
    """Funcion principal para resolver un puzzle Shikaku"""
    try:
        solver = ShikakuSolver(grid)
        solution = solver.solve()
        
        if solution:
            return solver.solution_to_dict(solution)
        
        return None
    except Exception as e:
        print(f"Error al resolver Shikaku: {e}")
        return None
