"""Pytest configuration and fixtures for Sudoku game tests."""

import pytest
import sys
import uuid
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from domain.models import SudokuBoard, GameState, BOARD_SIZE, EMPTY
from adapters.out.memory_repository import MemoryGameRepository
from adapters.out.puzzle_generator import RandomPuzzleGenerator
from services.game_service import GameService


@pytest.fixture
def flask_app():
    """Create and configure a Flask application for testing."""
    app = create_app({'TESTING': True})
    return app


@pytest.fixture
def client(flask_app):
    """Create a test client for the Flask application."""
    return flask_app.test_client()


@pytest.fixture
def app_context(flask_app):
    """Provide application context for tests."""
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def empty_board():
    """Create an empty 9x9 Sudoku board."""
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


@pytest.fixture
def sample_puzzle():
    """Create a sample puzzle for testing."""
    puzzle = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    # Add some clues
    puzzle[0][0] = 5
    puzzle[0][1] = 3
    puzzle[1][0] = 6
    return puzzle


@pytest.fixture
def sample_solution():
    """Create a complete Sudoku solution."""
    return [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]


@pytest.fixture
def game_repository():
    """Create a game repository for testing."""
    return MemoryGameRepository()


@pytest.fixture
def puzzle_generator():
    """Create a puzzle generator for testing."""
    return RandomPuzzleGenerator()


@pytest.fixture
def game_service(puzzle_generator, game_repository):
    """Create a game service with test dependencies."""
    return GameService(puzzle_generator, game_repository)


@pytest.fixture
def sample_game_state(sample_puzzle, sample_solution):
    """Create a sample game state for testing."""
    game_id = str(uuid.uuid4())
    puzzle_board = SudokuBoard(sample_puzzle)
    solution_board = SudokuBoard(sample_solution)
    current_board = puzzle_board.copy()
    
    return GameState(
        game_id=game_id,
        puzzle=puzzle_board,
        solution=solution_board,
        current_board=current_board,
        difficulty="medium"
    )
    return puzzle


@pytest.fixture
def sample_solution():
    """Create a sample complete solution for testing."""
    # A valid completed sudoku board
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    return solution
