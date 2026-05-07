from typing import List, Tuple, Dict, Optional

Grid = List[List[int]]


def rect_positions(r0: int, c0: int, h: int, w: int) -> List[Tuple[int, int]]:
    return [(r0 + dr, c0 + dc) for dr in range(h) for dc in range(w)]


def possible_rects_for_cell(rows: int, cols: int, r: int, c: int, area: int, grid: Grid) -> List[Tuple[int, int, int, int]]:
    # Retorna lista de rectangulos (r0,c0,h,w) con area que incluye (r,c)
    res = []
    for h in range(1, area + 1):
        if area % h != 0:
            continue
        w = area // h
        # Prueba posiciones donde el tope izquierdo (r0,c0) cumple r0<=r<r0+h y c0<=c<c0+w
        r0_min = max(0, r - h + 1)
        r0_max = min(r, rows - h)
        c0_min = max(0, c - w + 1)
        c0_max = min(c, cols - w)
        for r0 in range(r0_min, r0_max + 1):
            for c0 in range(c0_min, c0_max + 1):
                res.append((r0, c0, h, w))
    return res


def solve_shikaku(grid: Grid) -> Optional[List[Dict[str, int]]]:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    numbered = []
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] and grid[i][j] > 0:
                numbered.append((i, j, grid[i][j]))

    # Mapa de celdas asignadas
    assigned = [[None for _ in range(cols)] for _ in range(rows)]

    # Precalcula rectangulos por numero y filtra los que contienen otros numeros
    placements = {}
    for (r, c, area) in numbered:
        cand = []
        for (r0, c0, h, w) in possible_rects_for_cell(rows, cols, r, c, area, grid):
            coords = rect_positions(r0, c0, h, w)
            ok = True
            for (rr, cc) in coords:
                if grid[rr][cc] and grid[rr][cc] > 0 and not (rr == r and cc == c):
                    ok = False
                    break
            if ok:
                cand.append((r0, c0, h, w))
        if not cand:
            return None
        placements[(r, c)] = cand

    # Ordena numeros por menor cantidad de opciones (MRV)
    order = sorted(numbered, key=lambda x: len(placements[(x[0], x[1])]))

    solution = []

    def backtrack(idx: int) -> bool:
        if idx >= len(order):
            # Verifica cobertura total
            for i in range(rows):
                for j in range(cols):
                    if assigned[i][j] is None:
                        return False
            return True

        r, c, area = order[idx]
        key = (r, c)
        for (r0, c0, h, w) in placements[key]:
            coords = rect_positions(r0, c0, h, w)
            # Verifica celdas libres
            conflict = False
            for (rr, cc) in coords:
                if assigned[rr][cc] is not None:
                    conflict = True
                    break
            if conflict:
                continue
            # Asigna
            for (rr, cc) in coords:
                assigned[rr][cc] = key
            solution.append({"r0": r0, "c0": c0, "h": h, "w": w, "num_r": r, "num_c": c, "area": area})
            if backtrack(idx + 1):
                return True
            # Revierte
            solution.pop()
            for (rr, cc) in coords:
                assigned[rr][cc] = None
        return False

    ok = backtrack(0)
    if not ok:
        return None
    return solution
