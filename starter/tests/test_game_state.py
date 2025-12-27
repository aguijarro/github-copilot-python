"""Tests for GameState dataclass."""

import pytest
import time
from datetime import datetime, timedelta
from copy import deepcopy

from models.game_state import GameState
from domain.models import BOARD_SIZE, EMPTY


class TestGameStateInitialization:
    """Test GameState initialization."""
    
    def test_game_state_creation(self):
        """Test basic GameState instantiation."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        start_time = datetime.now()
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=start_time
        )
        
        assert gs.board == board
        assert gs.difficulty == 'medium'
        assert gs.start_time == start_time
        assert gs.hints_used == 0
        assert gs.is_complete is False
    
    def test_game_state_with_locked_cells(self):
        """Test GameState with initial locked cells."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[1][1] = 3
        
        gs = GameState(
            board=board,
            difficulty='easy',
            start_time=datetime.now()
        )
        
        assert (0, 0) in gs.locked_cells
        assert (1, 1) in gs.locked_cells
        assert len(gs.locked_cells) == 2
    
    def test_game_state_invalid_board_size(self):
        """Test that invalid board size raises error."""
        board = [[EMPTY for _ in range(8)] for _ in range(9)]  # Wrong size
        
        with pytest.raises(ValueError, match="must have 9 columns"):
            GameState(
                board=board,
                difficulty='medium',
                start_time=datetime.now()
            )
    
    def test_game_state_with_all_fields(self):
        """Test GameState creation with all fields."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        start_time = datetime.now()
        locked = [(0, 0), (1, 1), (2, 2)]
        
        gs = GameState(
            board=board,
            difficulty='hard',
            start_time=start_time,
            hints_used=3,
            locked_cells=locked,
            is_complete=False
        )
        
        assert gs.hints_used == 3
        assert gs.locked_cells == locked
        assert gs.is_complete is False


class TestIsCellLocked:
    """Test the is_cell_locked method."""
    
    def test_locked_cell_returns_true(self):
        """Test that locked cells return True."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        assert gs.is_cell_locked(0, 0) is True
    
    def test_empty_cell_returns_false(self):
        """Test that empty cells return False."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        assert gs.is_cell_locked(0, 1) is False
    
    def test_invalid_position_raises_error(self):
        """Test that invalid position raises ValueError."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        with pytest.raises(ValueError):
            gs.is_cell_locked(-1, 0)
        
        with pytest.raises(ValueError):
            gs.is_cell_locked(9, 0)


class TestCellCounting:
    """Test cell counting methods."""
    
    def test_get_locked_cells_count(self):
        """Test counting locked cells."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[1][1] = 3
        board[2][2] = 7
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        assert gs.get_locked_cells_count() == 3
    
    def test_get_filled_cells_count(self):
        """Test counting filled cells (locked + player-filled)."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[0][1] = 3
        board[1][0] = 7
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        assert gs.get_filled_cells_count() == 3
    
    def test_get_empty_cells_count(self):
        """Test counting empty cells."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        empty_count = gs.get_empty_cells_count()
        assert empty_count == BOARD_SIZE * BOARD_SIZE - 1
    
    def test_get_progress_percentage(self):
        """Test progress percentage calculation."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        # Fill 27 cells (3 rows worth)
        for i in range(3):
            for j in range(9):
                board[i][j] = (i * 9 + j) % 9 + 1
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        progress = gs.get_progress_percentage()
        expected = (27 / 81) * 100
        assert abs(progress - expected) < 0.01
    
    def test_progress_percentage_empty_board(self):
        """Test progress percentage with empty board."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        assert gs.get_progress_percentage() == 0.0
    
    def test_progress_percentage_full_board(self):
        """Test progress percentage with full board."""
        board = [[i % 9 + 1 for i in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        assert gs.get_progress_percentage() == 100.0


class TestElapsedTime:
    """Test the get_elapsed_time method."""
    
    def test_elapsed_time_immediate(self):
        """Test elapsed time right after creation."""
        gs = GameState(
            board=[[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            difficulty='medium',
            start_time=datetime.now()
        )
        
        elapsed = gs.get_elapsed_time()
        assert elapsed >= 0
        assert elapsed < 2  # Should be very close to 0
    
    def test_elapsed_time_increases(self):
        """Test that elapsed time increases over time."""
        gs = GameState(
            board=[[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            difficulty='medium',
            start_time=datetime.now() - timedelta(seconds=5)
        )
        
        elapsed = gs.get_elapsed_time()
        assert elapsed >= 5


class TestToDict:
    """Test the to_dict serialization method."""
    
    def test_to_dict_basic(self):
        """Test basic to_dict conversion."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        start_time = datetime.now()
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=start_time,
            hints_used=2
        )
        
        data = gs.to_dict()
        
        assert 'board' in data
        assert 'difficulty' in data
        assert 'start_time' in data
        assert 'hints_used' in data
        assert 'locked_cells' in data
        assert 'is_complete' in data
    
    def test_to_dict_datetime_serialization(self):
        """Test that datetime is serialized to ISO format string."""
        gs = GameState(
            board=[[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            difficulty='medium',
            start_time=datetime(2025, 12, 26, 10, 30, 45)
        )
        
        data = gs.to_dict()
        
        assert isinstance(data['start_time'], str)
        assert '2025-12-26' in data['start_time']
    
    def test_to_dict_locked_cells_serialization(self):
        """Test that locked_cells is serialized as list of lists."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[1][1] = 3
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        data = gs.to_dict()
        
        assert isinstance(data['locked_cells'], list)
        assert [0, 0] in data['locked_cells']
        assert [1, 1] in data['locked_cells']
    
    def test_to_dict_board_independence(self):
        """Test that to_dict returns independent board copy."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        data = gs.to_dict()
        data['board'][0][0] = 999
        
        # Original board should be unchanged
        assert gs.board[0][0] == 5


class TestFromDict:
    """Test the from_dict deserialization method."""
    
    def test_from_dict_basic(self):
        """Test basic from_dict conversion."""
        data = {
            'board': [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            'difficulty': 'medium',
            'start_time': datetime.now().isoformat(),
            'hints_used': 2,
            'locked_cells': [[0, 0], [1, 1]],
            'is_complete': False
        }
        
        gs = GameState.from_dict(data)
        
        assert gs.difficulty == 'medium'
        assert gs.hints_used == 2
        assert gs.is_complete is False
        assert len(gs.locked_cells) == 2
    
    def test_from_dict_datetime_parsing(self):
        """Test that ISO format string is parsed to datetime."""
        iso_time = datetime(2025, 12, 26, 10, 30, 45).isoformat()
        data = {
            'board': [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            'difficulty': 'medium',
            'start_time': iso_time,
            'locked_cells': [],
        }
        
        gs = GameState.from_dict(data)
        
        assert isinstance(gs.start_time, datetime)
        assert gs.start_time.year == 2025
    
    def test_from_dict_locked_cells_parsing(self):
        """Test that locked_cells are parsed as tuples."""
        data = {
            'board': [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            'difficulty': 'medium',
            'start_time': datetime.now().isoformat(),
            'locked_cells': [[0, 0], [1, 1], [2, 2]],
        }
        
        gs = GameState.from_dict(data)
        
        assert isinstance(gs.locked_cells, list)
        assert all(isinstance(cell, tuple) for cell in gs.locked_cells)
        assert (0, 0) in gs.locked_cells
        assert (1, 1) in gs.locked_cells
    
    def test_from_dict_missing_optional_fields(self):
        """Test from_dict with missing optional fields."""
        data = {
            'board': [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            'difficulty': 'medium',
            'start_time': datetime.now().isoformat(),
        }
        
        gs = GameState.from_dict(data)
        
        assert gs.hints_used == 0
        assert gs.is_complete is False
        assert gs.locked_cells == []
    
    def test_from_dict_missing_required_fields(self):
        """Test from_dict raises error with missing required fields."""
        data = {
            'difficulty': 'medium',
            'start_time': datetime.now().isoformat(),
        }
        
        with pytest.raises(KeyError):
            GameState.from_dict(data)


class TestRoundTripSerialization:
    """Test serialization and deserialization roundtrip."""
    
    def test_roundtrip_basic(self):
        """Test that data survives to_dict -> from_dict roundtrip."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[1][1] = 3
        start_time = datetime(2025, 12, 26, 10, 30, 45)
        
        original = GameState(
            board=board,
            difficulty='hard',
            start_time=start_time,
            hints_used=3,
            is_complete=False
        )
        
        data = original.to_dict()
        restored = GameState.from_dict(data)
        
        assert restored.board == original.board
        assert restored.difficulty == original.difficulty
        assert restored.start_time == original.start_time
        assert restored.hints_used == original.hints_used
        assert restored.is_complete == original.is_complete
        assert restored.locked_cells == original.locked_cells
    
    def test_roundtrip_with_many_locked_cells(self):
        """Test roundtrip with many locked cells."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        locked = []
        for i in range(5):
            board[i][i] = i + 1
            locked.append((i, i))
        
        original = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now(),
            locked_cells=locked
        )
        
        restored = GameState.from_dict(original.to_dict())
        
        assert len(restored.locked_cells) == len(original.locked_cells)
        assert set(restored.locked_cells) == set(original.locked_cells)


class TestCopy:
    """Test the copy method."""
    
    def test_copy_creates_independent_instance(self):
        """Test that copy creates independent GameState."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        original = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now(),
            hints_used=2
        )
        
        copy = original.copy()
        
        # Modify copy
        copy.board[0][0] = 999
        copy.hints_used = 10
        
        # Original should be unchanged
        assert original.board[0][0] == 5
        assert original.hints_used == 2
    
    def test_copy_preserves_all_fields(self):
        """Test that copy preserves all fields."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        start_time = datetime.now()
        locked = [(0, 0), (1, 1)]
        
        original = GameState(
            board=board,
            difficulty='hard',
            start_time=start_time,
            hints_used=3,
            locked_cells=locked,
            is_complete=False
        )
        
        copy = original.copy()
        
        assert copy.board == original.board
        assert copy.difficulty == original.difficulty
        assert copy.start_time == original.start_time
        assert copy.hints_used == original.hints_used
        assert copy.locked_cells == original.locked_cells
        assert copy.is_complete == original.is_complete


class TestLockUnlock:
    """Test lock_cell and unlock_cell methods."""
    
    def test_lock_cell(self):
        """Test locking a cell."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        result = gs.lock_cell(0, 0)
        
        assert result is True
        assert gs.is_cell_locked(0, 0) is True
    
    def test_lock_already_locked_cell(self):
        """Test locking an already locked cell returns False."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        result = gs.lock_cell(0, 0)
        
        assert result is False
    
    def test_unlock_cell(self):
        """Test unlocking a cell."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        result = gs.unlock_cell(0, 0)
        
        assert result is True
        assert gs.is_cell_locked(0, 0) is False
    
    def test_unlock_unlocked_cell(self):
        """Test unlocking an already unlocked cell returns False."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        result = gs.unlock_cell(0, 0)
        
        assert result is False
    
    def test_lock_unlock_invalid_position(self):
        """Test that lock/unlock with invalid position raises error."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        with pytest.raises(ValueError):
            gs.lock_cell(-1, 0)
        
        with pytest.raises(ValueError):
            gs.unlock_cell(9, 0)


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_board_with_all_different_values(self):
        """Test board filled with different values."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                board[i][j] = (i + j) % 9 + 1
        
        gs = GameState(
            board=board,
            difficulty='expert',
            start_time=datetime.now()
        )
        
        assert gs.get_filled_cells_count() == BOARD_SIZE * BOARD_SIZE
        assert gs.get_empty_cells_count() == 0
        assert gs.get_progress_percentage() == 100.0
    
    def test_empty_board(self):
        """Test completely empty board."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        gs = GameState(
            board=board,
            difficulty='easy',
            start_time=datetime.now()
        )
        
        assert gs.get_locked_cells_count() == 0
        assert gs.get_filled_cells_count() == 0
        assert gs.get_empty_cells_count() == BOARD_SIZE * BOARD_SIZE
        assert gs.get_progress_percentage() == 0.0
    
    def test_single_clue_board(self):
        """Test board with single clue."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[4][4] = 5
        
        gs = GameState(
            board=board,
            difficulty='expert',
            start_time=datetime.now()
        )
        
        assert gs.get_locked_cells_count() == 1
        assert gs.get_progress_percentage() > 0.0
    
    def test_to_dict_and_back_with_all_difficulties(self):
        """Test serialization with all difficulty levels."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        for difficulty in ['easy', 'medium', 'hard', 'expert']:
            gs = GameState(
                board=board,
                difficulty=difficulty,
                start_time=datetime.now()
            )
            
            restored = GameState.from_dict(gs.to_dict())
            assert restored.difficulty == difficulty


class TestIntegration:
    """Integration tests combining multiple methods."""
    
    def test_game_progression(self):
        """Test a typical game progression scenario."""
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[0][1] = 3
        
        gs = GameState(
            board=board,
            difficulty='medium',
            start_time=datetime.now()
        )
        
        # Initial state
        assert gs.get_locked_cells_count() == 2
        assert gs.get_progress_percentage() < 10
        assert gs.hints_used == 0
        
        # Player fills some cells
        gs.board[1][1] = 7
        gs.board[2][2] = 9
        
        # Progress increases
        assert gs.get_filled_cells_count() == 4
        assert gs.get_progress_percentage() > 4
        
        # Player uses hints
        gs.hints_used = 2
        
        # Serialize and restore
        data = gs.to_dict()
        restored = GameState.from_dict(data)
        
        assert restored.hints_used == 2
        assert restored.get_filled_cells_count() == 4
        assert restored.get_locked_cells_count() == 2
