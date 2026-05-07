"""
Example demonstrations of the Shikaku solver
"""

from app.shikaku_solver import ShikakuSolver, solve_shikaku
import json


def print_grid(grid):
    """Pretty print a Shikaku grid"""
    print("\nPuzzle Grid:")
    for row in grid:
        print(" ".join(f"{cell:2}" if cell > 0 else " ." for cell in row))


def print_solution(grid, solution):
    """Print solution with rectangle assignments"""
    if not solution:
        print("No solution found!")
        return
    
    # Create visual grid with rectangle IDs
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    rect_grid = [[-1 for _ in range(cols)] for _ in range(rows)]
    
    for idx, rect_dict in enumerate(solution):
        for r, c in rect_dict['cells']:
            rect_grid[r][c] = idx
    
    print("\nSolution (rectangle assignments):")
    for row in rect_grid:
        print(" ".join(f"{cell:2}" for cell in row))
    
    print("\nRectangle Details:")
    for idx, rect_dict in enumerate(solution):
        print(f"  Rect {idx}: position ({rect_dict['row']},{rect_dict['col']}), "
              f"size {rect_dict['height']}x{rect_dict['width']}, "
              f"area={rect_dict['height']*rect_dict['width']}, number={rect_dict['number']}")


def example_1():
    """Simple 2x2 example"""
    print("\n" + "="*50)
    print("EXAMPLE 1: Simple 2x2 Puzzle")
    print("="*50)
    
    grid = [
        [2, 0],
        [0, 2]
    ]
    
    print_grid(grid)
    solution = solve_shikaku(grid)
    print_solution(grid, solution)


def example_2():
    """2x3 rectangle puzzle"""
    print("\n" + "="*50)
    print("EXAMPLE 2: 2x3 Rectangle Puzzle")
    print("="*50)
    
    grid = [
        [4, 0, 2],
        [0, 0, 0]
    ]
    
    print_grid(grid)
    solution = solve_shikaku(grid)
    print_solution(grid, solution)


def example_3():
    """3x3 puzzle"""
    print("\n" + "="*50)
    print("EXAMPLE 3: 3x3 Puzzle")
    print("="*50)
    
    grid = [
        [2, 0, 3],
        [0, 0, 0],
        [4, 0, 0]
    ]
    
    print_grid(grid)
    solution = solve_shikaku(grid)
    print_solution(grid, solution)


def example_4():
    """4x4 puzzle - more complex"""
    print("\n" + "="*50)
    print("EXAMPLE 4: 4x4 Puzzle (Complex)")
    print("="*50)
    
    grid = [
        [4, 0, 0, 2],
        [0, 0, 0, 0],
        [0, 2, 0, 2],
        [0, 0, 0, 0]
    ]
    
    print_grid(grid)
    solution = solve_shikaku(grid)
    print_solution(grid, solution)


def example_5():
    """Performance test with larger grid"""
    print("\n" + "="*50)
    print("EXAMPLE 5: Performance Test (5x5)")
    print("="*50)
    
    grid = [
        [2, 0, 3, 0, 0],
        [0, 0, 0, 0, 0],
        [4, 0, 0, 0, 2],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 4]
    ]
    
    print_grid(grid)
    
    import time
    start = time.time()
    solution = solve_shikaku(grid)
    elapsed = time.time() - start
    
    print_solution(grid, solution)
    print(f"Solved in {elapsed:.4f} seconds")


if __name__ == "__main__":
    print("\nSHIKAKU SOLVER - DEMONSTRATION")
    print("=" * 50)
    
    # Run examples
    example_1()
    example_2()
    example_3()
    example_4()
    example_5()
    
    print("\n" + "="*50)
    print("All examples completed!")
