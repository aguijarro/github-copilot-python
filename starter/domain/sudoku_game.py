"""Core Sudoku game logic - pure business domain."""

from typing import List, Tuple
import random

from .models import SudokuBoard, BOARD_SIZE, EMPTY
from .exceptions import PuzzleGenerationError


def is_safe_in_row(board: List[List[int]], row: int, num: int) -> bool:
    """Check if num is not in the given row.
    
    Args:
        board: 9x9 Sudoku grid
        row: Row index (0-8)
        num: Number to check (1-9)
    
    Returns:
        True if number is not in row
    """
    return num not in board[row]


def is_safe_in_column(board: List[List[int]], col: int, num: int) -> bool:
    """Check if num is not in the given column.
    
    Args:
        board: 9x9 Sudoku grid
        col: Column index (0-8)
        num: Number to check (1-9)
    
    Returns:
        True if number is not in column
    """
    return num not in [board[row][col] for row in range(BOARD_SIZE)]


def is_safe_in_box(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Check if num is not in the 3x3 box containing (row, col).
    
    Args:
        board: 9x9 Sudoku grid
        row: Row index (0-8)
        col: Column index (0-8)
        num: Number to check (1-9)
    
    Returns:
        True if number is not in 3x3 box
    """
    box_row, box_col = (row // 3) * 3, (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[box_row + i][box_col + j] == num:
                return False
    return True


def is_safe(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Check if placing num at (row, col) is valid per Sudoku rules.
    
    Args:
        board: 9x9 Sudoku grid
        row: Row index (0-8)
        col: Column index (0-8)
        num: Number to place (1-9)
    
    Returns:
        True if placement is valid
    """
    return (is_safe_in_row(board, row, num) and
            is_safe_in_column(board, col, num) and
            is_safe_in_box(board, row, col, num))


def create_empty_board() -> List[List[int]]:
    """Create an empty 9x9 Sudoku board.
    
    Returns:
        9x9 board filled with zeros (empty cells)
    """
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def fill_solution_board(board: List[List[int]]) -> bool:
    """Fill empty board with valid Sudoku solution using backtracking.
    
    Args:
        board: Empty 9x9 Sudoku board (modified in place)
    
    Returns:
        True if board was successfully filled
    
    Raises:
        PuzzleGenerationError: If board cannot be filled
    """
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == EMPTY:
                candidates = list(range(1, BOARD_SIZE + 1))
                random.shuffle(candidates)
                for num in candidates:
                    if is_safe(board, row, col, num):
                        board[row][col] = num
                        if fill_solution_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_clues(board: List[List[int]], target_clues: int) -> None:
    """Remove clues from completed board to create puzzle.
    
    Args:
        board: Completed 9x9 Sudoku board (modified in place)
        target_clues: Number of clues to leave visible
    
    Raises:
        ValueError: If target_clues is invalid
    """
    if not (17 <= target_clues <= 81):
        raise ValueError("Target clues must be between 17 and 81")
    
    cells_to_remove = BOARD_SIZE * BOARD_SIZE - target_clues
    removed = 0
    
    while removed < cells_to_remove:
        row = random.randrange(BOARD_SIZE)
        col = random.randrange(BOARD_SIZE)
        
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            removed += 1


def generate_puzzle(clues: int = 35) -> Tuple[List[List[int]], List[List[int]]]:
    """Generate a valid Sudoku puzzle with unique solution.
    
    Args:
        clues: Number of clues (visible numbers) in puzzle (17-81)
    
    Returns:
        Tuple of (puzzle, solution) boards
    
    Raises:
        PuzzleGenerationError: If puzzle cannot be generated
        ValueError: If clue count is invalid
    """
    if not (17 <= clues <= 81):
        raise ValueError("Clue count must be between 17 and 81")
    
    try:
        # Create and fill solution board
        solution_board = create_empty_board()
        if not fill_solution_board(solution_board):
            raise PuzzleGenerationError("Failed to fill solution board")
        
        # Create puzzle by removing clues from solution
        puzzle_board = [row[:] for row in solution_board]
        remove_clues(puzzle_board, clues)
        
        return puzzle_board, solution_board
    
    except Exception as e:
        if isinstance(e, (ValueError, PuzzleGenerationError)):
            raise
        raise PuzzleGenerationError(f"Puzzle generation failed: {str(e)}")


def validate_move(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Validate if a move is legal in the current game state.
    
    Args:
        board: Current game board
        row: Row index (0-8)
        col: Column index (0-8)
        num: Number to place (1-9)
    
    Returns:
        True if move is valid
    
    Raises:
        ValueError: If position or number is invalid
    """
    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        raise ValueError(f"Invalid position: ({row}, {col})")
    if not (1 <= num <= BOARD_SIZE):
        raise ValueError(f"Invalid number: {num}")
    
    if board[row][col] != EMPTY:
        raise ValueError(f"Cell ({row}, {col}) is not empty")
    
    return is_safe(board, row, col, num)


def find_incorrect_cells(current: List[List[int]], solution: List[List[int]]) -> List[Tuple[int, int]]:
    """Find all cells where current board differs from solution.
    
    Args:
        current: Current game board
        solution: Solution board
    
    Returns:
        List of (row, col) tuples for incorrect cells
    """
    incorrect = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if current[row][col] != solution[row][col]:
                incorrect.append((row, col))
    return incorrect
