"""Pytest configuration and fixtures for Flask Sudoku app."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import app
from sudoku_logic import create_empty_board, SIZE


@pytest.fixture
def flask_app():
    """Create and configure a Flask application for testing."""
    app.app.config['TESTING'] = True
    return app.app


@pytest.fixture
def client(flask_app):
    """Create a test client for the Flask application."""
    # Reset CURRENT state before each test
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None
    return flask_app.test_client()


@pytest.fixture
def app_context(flask_app):
    """Provide application context for tests."""
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def empty_board():
    """Create an empty 9x9 Sudoku board."""
    return create_empty_board()


@pytest.fixture
def sample_puzzle():
    """Create a sample puzzle for testing."""
    puzzle = create_empty_board()
    # Add some clues to make it a valid puzzle
    puzzle[0][0] = 5
    puzzle[0][1] = 3
    puzzle[1][0] = 6
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
