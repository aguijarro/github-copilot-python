"""Unit tests for game service layer."""

import pytest
import uuid
from services.game_service import GameService
from domain.models import GameState
from domain.exceptions import GameNotFoundError
from adapters.out.puzzle_generator import RandomPuzzleGenerator
from adapters.out.memory_repository import MemoryGameRepository


class TestGameService:
    """Tests for GameService."""
    
    def test_start_new_game(self, game_service):
        """Test starting a new game."""
        game_id = str(uuid.uuid4())
        puzzle = game_service.start_new_game(game_id, 35)
        
        assert isinstance(puzzle, list)
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)
    
    def test_start_new_game_saves_state(self, game_service):
        """Test that new game saves state to repository."""
        game_id = str(uuid.uuid4())
        game_service.start_new_game(game_id, 35)
        
        state = game_service.get_game_state(game_id)
        assert state is not None
        assert state.game_id == game_id
    
    def test_check_solution_correct(self, game_service):
        """Test checking a correct solution."""
        game_id = str(uuid.uuid4())
        game_service.start_new_game(game_id, 35)
        
        # Get the correct solution from the saved game state
        game_state = game_service.get_game_state(game_id)
        correct_board = [row[:] for row in game_state.solution.grid]
        
        result = game_service.check_solution(game_id, correct_board)
        assert result.is_correct
        assert len(result.incorrect_cells) == 0
    
    def test_check_solution_incorrect(self, game_service, sample_solution):
        """Test checking an incorrect solution."""
        game_id = str(uuid.uuid4())
        game_service.start_new_game(game_id, 35)
        
        # Create a board with wrong values
        wrong_solution = [row[:] for row in sample_solution]
        wrong_solution[0][0] = 9
        wrong_solution[0][1] = 9
        
        result = game_service.check_solution(game_id, wrong_solution)
        assert not result.is_correct
        assert len(result.incorrect_cells) > 0
    
    def test_check_solution_game_not_found(self, game_service, sample_solution):
        """Test checking solution for non-existent game."""
        with pytest.raises(GameNotFoundError):
            game_service.check_solution('nonexistent', sample_solution)
    
    def test_get_game_state_exists(self, game_service):
        """Test retrieving existing game state."""
        game_id = str(uuid.uuid4())
        game_service.start_new_game(game_id, 35)
        
        state = game_service.get_game_state(game_id)
        assert state.game_id == game_id
    
    def test_get_game_state_not_found(self, game_service):
        """Test retrieving non-existent game state."""
        with pytest.raises(GameNotFoundError):
            game_service.get_game_state('nonexistent')
    
    def test_save_game(self, game_service, sample_game_state):
        """Test saving game state."""
        game_service.repository.save(sample_game_state.game_id, sample_game_state)
        
        retrieved = game_service.get_game_state(sample_game_state.game_id)
        assert retrieved.game_id == sample_game_state.game_id
