"""Game service - orchestrates use cases."""

from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import random

from domain.models import GameState, SudokuBoard, CheckResult, BOARD_SIZE, EMPTY
from domain.sudoku_game import find_incorrect_cells
from domain.exceptions import GameNotFoundError, ValidationError
from ports.puzzle_generator import PuzzleGenerator
from ports.game_repository import GameRepository


class GameService:
    """Service for game use cases.
    
    Orchestrates interactions between domain logic, ports, and adapters.
    """
    
    def __init__(self, puzzle_generator: PuzzleGenerator, repository: GameRepository):
        """Initialize GameService with dependencies.
        
        Args:
            puzzle_generator: Implementation of PuzzleGenerator port
            repository: Implementation of GameRepository port
        """
        self.puzzle_generator = puzzle_generator
        self.repository = repository
    
    def start_new_game(self, game_id: str, clues: int) -> List[List[int]]:
        """Start a new Sudoku game.
        
        Args:
            game_id: Unique identifier for the game
            clues: Number of visible clues (17-81)
        
        Returns:
            Puzzle board as 2D list
        
        Raises:
            ValueError: If clues is invalid
        """
        # Generate puzzle using port
        puzzle, solution = self.puzzle_generator.generate(clues)
        
        # Create game state
        puzzle_board = SudokuBoard(puzzle)
        solution_board = SudokuBoard(solution)
        current_board = puzzle_board.copy()
        
        game_state = GameState(
            game_id=game_id,
            puzzle=puzzle_board,
            solution=solution_board,
            current_board=current_board,
            difficulty="medium"
        )
        
        # Save game state using port
        self.repository.save(game_id, game_state)
        
        return puzzle
    
    def check_solution(self, game_id: str, board: List[List[int]]) -> CheckResult:
        """Check if solution is correct.
        
        Args:
            game_id: Game identifier
            board: Current board state (9x9 2D list)
        
        Returns:
            CheckResult with correctness status and incorrect cells
        
        Raises:
            GameNotFoundError: If game not found
            ValidationError: If board is invalid
        """
        # Load game state
        game_state = self.repository.load(game_id)
        if not game_state:
            raise GameNotFoundError(f"Game {game_id} not found")
        
        # Find incorrect cells by comparing with solution
        solution_grid = game_state.solution.grid
        incorrect_cells = find_incorrect_cells(board, solution_grid)
        
        # Check if puzzle is complete and correct
        is_complete = all(cell != EMPTY for row in board for cell in row)
        is_correct = is_complete and len(incorrect_cells) == 0
        
        return CheckResult(
            is_correct=is_correct,
            incorrect_cells=incorrect_cells,
            message="Correct!" if is_correct else ""
        )
    
    def get_game_state(self, game_id: str) -> GameState:
        """Get current game state.
        
        Args:
            game_id: Game identifier
        
        Returns:
            GameState
        
        Raises:
            GameNotFoundError: If game not found
        """
        game_state = self.repository.load(game_id)
        if not game_state:
            raise GameNotFoundError(f"Game {game_id} not found")
        return game_state
    
    def save_game(self, game_id: str, game_state: GameState) -> None:
        """Save game state.
        
        Args:
            game_id: Game identifier
            game_state: Game state to save
        """
        game_state.updated_at = datetime.now()
        self.repository.save(game_id, game_state)
    
    def get_hint(self, game_id: str, current_board: List[List[int]]) -> Dict[str, Any]:
        """Get a hint by filling a random empty cell with its solution value.
        
        Args:
            game_id: Game identifier
            current_board: Current board state (9x9 2D list)
        
        Returns:
            Dict with keys:
                - row: Row index of hinted cell
                - col: Column index of hinted cell
                - value: Correct value for that cell
                - hints_used: Updated hint count
        
        Raises:
            GameNotFoundError: If game not found
            ValidationError: If no empty cells remain
        """
        # Load game state
        game_state = self.repository.load(game_id)
        if not game_state:
            raise GameNotFoundError(f"Game {game_id} not found")
        
        # Find all empty cells
        empty_cells = [
            (row, col)
            for row in range(BOARD_SIZE)
            for col in range(BOARD_SIZE)
            if current_board[row][col] == EMPTY
        ]
        
        if not empty_cells:
            raise ValidationError("No empty cells remaining - puzzle is complete!")
        
        # Select random empty cell
        row, col = random.choice(empty_cells)
        
        # Get correct value from solution
        solution_value = game_state.solution.get_cell(row, col)
        
        # Update current board with hint value
        current_board[row][col] = solution_value
        
        # Update game state
        game_state.current_board.set_cell(row, col, solution_value)
        game_state.locked_cells.append((row, col))
        game_state.moves += 1
        
        # Increment hints used counter
        if not hasattr(game_state, 'hints_used'):
            game_state.hints_used = 0
        game_state.hints_used += 1
        
        # Save updated game state
        self.save_game(game_id, game_state)
        
        return {
            'row': row,
            'col': col,
            'value': solution_value,
            'hints_used': game_state.hints_used
        }
