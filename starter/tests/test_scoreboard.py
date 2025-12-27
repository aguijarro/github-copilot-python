"""Tests for Scoreboard model."""

import pytest
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from models.scoreboard import Scoreboard, Score


class TestScoreInitialization:
    """Test Score dataclass initialization."""
    
    def test_score_creation(self):
        """Test basic Score instantiation."""
        date = datetime.now()
        score = Score(
            name='Alice',
            time=300,
            difficulty='medium',
            hints=2,
            date=date
        )
        
        assert score.name == 'Alice'
        assert score.time == 300
        assert score.difficulty == 'medium'
        assert score.hints == 2
        assert score.date == date
    
    def test_score_with_default_date(self):
        """Test Score with default date."""
        score = Score(
            name='Bob',
            time=450,
            difficulty='hard',
            hints=0
        )
        
        assert score.name == 'Bob'
        assert isinstance(score.date, datetime)
        assert score.date.year == datetime.now().year
    
    def test_score_invalid_name(self):
        """Test Score with invalid name."""
        with pytest.raises(ValueError, match="Name must be a non-empty string"):
            Score(name='', time=300, difficulty='easy', hints=1)
        
        with pytest.raises(ValueError, match="Name must be a non-empty string"):
            Score(name=None, time=300, difficulty='easy', hints=1)
    
    def test_score_invalid_time(self):
        """Test Score with negative time."""
        with pytest.raises(ValueError, match="Time must be non-negative"):
            Score(name='Alice', time=-100, difficulty='easy', hints=1)
    
    def test_score_invalid_hints(self):
        """Test Score with negative hints."""
        with pytest.raises(ValueError, match="Hints must be non-negative"):
            Score(name='Alice', time=300, difficulty='easy', hints=-1)
    
    def test_score_invalid_difficulty(self):
        """Test Score with invalid difficulty."""
        with pytest.raises(ValueError, match="Invalid difficulty"):
            Score(name='Alice', time=300, difficulty='impossible', hints=1)
    
    def test_score_valid_difficulties(self):
        """Test Score with all valid difficulties."""
        for difficulty in ('easy', 'medium', 'hard', 'expert'):
            score = Score(
                name='Alice',
                time=300,
                difficulty=difficulty,
                hints=0
            )
            assert score.difficulty == difficulty


class TestScoreSerialization:
    """Test Score serialization and deserialization."""
    
    def test_score_to_dict(self):
        """Test converting Score to dictionary."""
        date = datetime(2025, 12, 27, 10, 30, 0)
        score = Score(
            name='Alice',
            time=300,
            difficulty='medium',
            hints=2,
            date=date
        )
        
        score_dict = score.to_dict()
        
        assert score_dict['name'] == 'Alice'
        assert score_dict['time'] == 300
        assert score_dict['difficulty'] == 'medium'
        assert score_dict['hints'] == 2
        assert score_dict['date'] == '2025-12-27T10:30:00'
    
    def test_score_from_dict(self):
        """Test creating Score from dictionary."""
        data = {
            'name': 'Bob',
            'time': 450,
            'difficulty': 'hard',
            'hints': 0,
            'date': '2025-12-27T10:30:00'
        }
        
        score = Score.from_dict(data)
        
        assert score.name == 'Bob'
        assert score.time == 450
        assert score.difficulty == 'hard'
        assert score.hints == 0
        assert score.date.year == 2025


class TestScoreboardInitialization:
    """Test Scoreboard initialization."""
    
    def test_scoreboard_creation_new_file(self):
        """Test creating Scoreboard with non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'scores.json')
            scoreboard = Scoreboard(storage_path=storage_path)
            
            assert scoreboard.scores == []
            assert scoreboard.storage_path == storage_path
    
    def test_scoreboard_creation_existing_file(self):
        """Test creating Scoreboard with existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'scores.json')
            
            # Create initial file
            initial_scores = [
                {'name': 'Alice', 'time': 300, 'difficulty': 'medium', 'hints': 2,
                 'date': '2025-12-27T10:30:00'},
                {'name': 'Bob', 'time': 450, 'difficulty': 'hard', 'hints': 0,
                 'date': '2025-12-27T10:35:00'}
            ]
            Path(tmpdir).mkdir(exist_ok=True)
            with open(storage_path, 'w') as f:
                json.dump(initial_scores, f)
            
            # Load from existing file
            scoreboard = Scoreboard(storage_path=storage_path)
            
            assert len(scoreboard.scores) == 2
            assert scoreboard.scores[0].name == 'Alice'
            assert scoreboard.scores[1].name == 'Bob'


class TestScoreboardAddScore:
    """Test adding scores to Scoreboard."""
    
    @pytest.fixture
    def scoreboard(self):
        """Create a temporary Scoreboard for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'scores.json')
            yield Scoreboard(storage_path=storage_path)
    
    def test_add_single_score(self, scoreboard):
        """Test adding a single score."""
        score = scoreboard.add_score('Alice', 300, 'medium', 2)
        
        assert score.name == 'Alice'
        assert score.time == 300
        assert score.difficulty == 'medium'
        assert score.hints == 2
        assert len(scoreboard.scores) == 1
    
    def test_add_multiple_scores(self, scoreboard):
        """Test adding multiple scores."""
        scoreboard.add_score('Alice', 300, 'medium', 2)
        scoreboard.add_score('Bob', 450, 'hard', 0)
        scoreboard.add_score('Charlie', 200, 'easy', 5)
        
        assert len(scoreboard.scores) == 3
    
    def test_add_score_persists(self, scoreboard):
        """Test that added score is persisted to file."""
        scoreboard.add_score('Alice', 300, 'medium', 2)
        
        # Verify file exists and contains the score
        assert os.path.exists(scoreboard.storage_path)
        with open(scoreboard.storage_path, 'r') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]['name'] == 'Alice'
    
    def test_add_score_invalid_params(self, scoreboard):
        """Test adding score with invalid parameters."""
        with pytest.raises(ValueError):
            scoreboard.add_score('', 300, 'medium', 2)
        
        with pytest.raises(ValueError):
            scoreboard.add_score('Alice', -10, 'medium', 2)
        
        with pytest.raises(ValueError):
            scoreboard.add_score('Alice', 300, 'invalid', 2)


class TestScoreboardGetTopScores:
    """Test retrieving top scores."""
    
    @pytest.fixture
    def scoreboard_with_scores(self):
        """Create Scoreboard with sample scores."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'scores.json')
            scoreboard = Scoreboard(storage_path=storage_path)
            
            # Add scores with different times
            scoreboard.add_score('Alice', 300, 'medium', 2)
            scoreboard.add_score('Bob', 450, 'hard', 0)
            scoreboard.add_score('Charlie', 200, 'easy', 5)
            scoreboard.add_score('Diana', 250, 'medium', 1)
            scoreboard.add_score('Eve', 500, 'hard', 3)
            
            yield scoreboard
    
    def test_get_top_10_all_scores(self, scoreboard_with_scores):
        """Test getting top 10 when there are fewer than 10 scores."""
        top_10 = scoreboard_with_scores.get_top_10()
        
        assert len(top_10) == 5
        # Should be sorted by time ascending (fastest first)
        assert top_10[0].name == 'Charlie'  # 200s
        assert top_10[1].name == 'Diana'    # 250s
        assert top_10[2].name == 'Alice'    # 300s
        assert top_10[3].name == 'Bob'      # 450s
        assert top_10[4].name == 'Eve'      # 500s
    
    def test_get_top_10_more_than_10_scores(self):
        """Test getting top 10 when there are more than 10 scores."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'scores.json')
            scoreboard = Scoreboard(storage_path=storage_path)
            
            # Add 15 scores
            for i in range(15):
                scoreboard.add_score(f'Player{i}', 100 + i * 10, 'easy', 0)
            
            top_10 = scoreboard.get_top_10()
            
            assert len(top_10) == 10
            assert top_10[0].time == 100
            assert top_10[9].time == 190
    
    def test_get_top_10_empty_scoreboard(self):
        """Test getting top 10 from empty scoreboard."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'scores.json')
            scoreboard = Scoreboard(storage_path=storage_path)
            
            top_10 = scoreboard.get_top_10()
            
            assert top_10 == []


class TestScoreboardFiltering:
    """Test filtering scores by difficulty."""
    
    @pytest.fixture
    def scoreboard_with_scores(self):
        """Create Scoreboard with scores of different difficulties."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'scores.json')
            scoreboard = Scoreboard(storage_path=storage_path)
            
            scoreboard.add_score('Alice', 300, 'easy', 2)
            scoreboard.add_score('Bob', 250, 'easy', 0)
            scoreboard.add_score('Charlie', 450, 'medium', 1)
            scoreboard.add_score('Diana', 400, 'medium', 3)
            scoreboard.add_score('Eve', 600, 'hard', 5)
            
            yield scoreboard
    
    def test_get_scores_by_difficulty(self, scoreboard_with_scores):
        """Test filtering scores by difficulty."""
        easy_scores = scoreboard_with_scores.get_scores_by_difficulty('easy')
        
        assert len(easy_scores) == 2
        assert all(s.difficulty == 'easy' for s in easy_scores)
    
    def test_get_top_10_by_difficulty(self, scoreboard_with_scores):
        """Test getting top 10 by difficulty."""
        medium_top = scoreboard_with_scores.get_top_10_by_difficulty('medium')
        
        assert len(medium_top) == 2
        assert medium_top[0].time == 400
        assert medium_top[1].time == 450
    
    def test_get_top_10_by_difficulty_empty(self, scoreboard_with_scores):
        """Test getting top 10 for difficulty with no scores."""
        expert_top = scoreboard_with_scores.get_top_10_by_difficulty('expert')
        
        assert expert_top == []


class TestScoreboardPersistence:
    """Test saving and loading scores."""
    
    def test_save_and_load_scores(self):
        """Test that scores persist across Scoreboard instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'scores.json')
            
            # Create scoreboard and add scores
            scoreboard1 = Scoreboard(storage_path=storage_path)
            scoreboard1.add_score('Alice', 300, 'medium', 2)
            scoreboard1.add_score('Bob', 450, 'hard', 0)
            
            # Create new scoreboard and load from file
            scoreboard2 = Scoreboard(storage_path=storage_path)
            
            assert len(scoreboard2.scores) == 2
            assert scoreboard2.scores[0].name == 'Alice'
            assert scoreboard2.scores[1].name == 'Bob'
    
    def test_load_corrupted_file(self):
        """Test loading from corrupted JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'scores.json')
            
            # Create corrupted file
            with open(storage_path, 'w') as f:
                f.write('invalid json{')
            
            with pytest.raises(IOError, match="Failed to load scores"):
                Scoreboard(storage_path=storage_path)
    
    def test_save_to_nonexistent_directory(self):
        """Test that directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'subdir', 'data', 'scores.json')
            
            scoreboard = Scoreboard(storage_path=storage_path)
            scoreboard.add_score('Alice', 300, 'medium', 2)
            
            assert os.path.exists(storage_path)


class TestScoreboardUtilities:
    """Test utility methods."""
    
    @pytest.fixture
    def scoreboard_with_scores(self):
        """Create Scoreboard with sample scores."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, 'scores.json')
            scoreboard = Scoreboard(storage_path=storage_path)
            
            scoreboard.add_score('Alice', 300, 'medium', 2)
            scoreboard.add_score('Bob', 450, 'hard', 0)
            scoreboard.add_score('Charlie', 200, 'easy', 5)
            
            yield scoreboard
    
    def test_get_all_scores(self, scoreboard_with_scores):
        """Test getting all scores."""
        all_scores = scoreboard_with_scores.get_all_scores()
        
        assert len(all_scores) == 3
        # Verify it's a copy, not the same list
        all_scores.clear()
        assert len(scoreboard_with_scores.scores) == 3
    
    def test_clear_all(self, scoreboard_with_scores):
        """Test clearing all scores."""
        scoreboard_with_scores.clear_all()
        
        assert len(scoreboard_with_scores.scores) == 0
        assert os.path.exists(scoreboard_with_scores.storage_path)
        
        # Verify cleared state persists
        with open(scoreboard_with_scores.storage_path, 'r') as f:
            data = json.load(f)
        assert data == []
