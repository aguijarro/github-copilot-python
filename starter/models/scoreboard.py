"""Scoreboard model for managing player scores."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path


@dataclass
class Score:
    """Represents a single score entry.
    
    Attributes:
        name: Player name
        time: Time taken to complete the puzzle (in seconds)
        difficulty: Difficulty level ('easy', 'medium', 'hard', 'expert')
        hints: Number of hints used
        date: Timestamp when the score was recorded
    """
    name: str
    time: int
    difficulty: str
    hints: int
    date: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate score values."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Name must be a non-empty string")
        if self.time < 0:
            raise ValueError("Time must be non-negative")
        if self.hints < 0:
            raise ValueError("Hints must be non-negative")
        if self.difficulty not in ('easy', 'medium', 'hard', 'expert'):
            raise ValueError(f"Invalid difficulty: {self.difficulty}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert score to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'time': self.time,
            'difficulty': self.difficulty,
            'hints': self.hints,
            'date': self.date.isoformat()
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Score':
        """Create Score from dictionary."""
        return Score(
            name=data['name'],
            time=data['time'],
            difficulty=data['difficulty'],
            hints=data['hints'],
            date=datetime.fromisoformat(data['date']) if isinstance(data['date'], str) else data['date']
        )


class Scoreboard:
    """Manages player scores with persistence to localStorage (JSON file).
    
    Provides functionality to add scores, retrieve top 10, and persist
    scores to local storage (JSON file).
    """
    
    def __init__(self, storage_path: str = 'data/scores.json'):
        """Initialize Scoreboard with optional custom storage path.
        
        Args:
            storage_path: Path to JSON file for score storage. Defaults to 'data/scores.json'
        """
        self.storage_path = storage_path
        self.scores: List[Score] = []
        self.load_from_localStorage()
    
    def add_score(self, name: str, time: int, difficulty: str, hints: int) -> Score:
        """Add a new score to the scoreboard.
        
        Args:
            name: Player name
            time: Time taken in seconds
            difficulty: Difficulty level
            hints: Number of hints used
            
        Returns:
            The created Score object
            
        Raises:
            ValueError: If any score parameter is invalid
        """
        score = Score(
            name=name,
            time=time,
            difficulty=difficulty,
            hints=hints,
            date=datetime.now()
        )
        self.scores.append(score)
        self.save_to_localStorage()
        return score
    
    def get_top_10(self) -> List[Score]:
        """Get top 10 scores sorted by time (fastest first).
        
        Returns:
            List of top 10 Score objects sorted by time ascending
        """
        sorted_scores = sorted(self.scores, key=lambda s: s.time)
        return sorted_scores[:10]
    
    def get_scores_by_difficulty(self, difficulty: str) -> List[Score]:
        """Get all scores for a specific difficulty level.
        
        Args:
            difficulty: Difficulty level to filter by
            
        Returns:
            List of Score objects for the specified difficulty
        """
        return [s for s in self.scores if s.difficulty == difficulty]
    
    def get_top_10_by_difficulty(self, difficulty: str) -> List[Score]:
        """Get top 10 scores for a specific difficulty level.
        
        Args:
            difficulty: Difficulty level to filter by
            
        Returns:
            List of top 10 Score objects for the specified difficulty
        """
        filtered = self.get_scores_by_difficulty(difficulty)
        sorted_scores = sorted(filtered, key=lambda s: s.time)
        return sorted_scores[:10]
    
    def save_to_localStorage(self) -> None:
        """Save all scores to localStorage (JSON file).
        
        Creates the data directory if it doesn't exist.
        """
        # Ensure data directory exists
        Path(os.path.dirname(self.storage_path) or '.').mkdir(
            parents=True, exist_ok=True
        )
        
        # Convert scores to dictionaries for JSON serialization
        scores_data = [score.to_dict() for score in self.scores]
        
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(scores_data, f, indent=2)
        except IOError as e:
            raise IOError(f"Failed to save scores to {self.storage_path}: {e}")
    
    def load_from_localStorage(self) -> None:
        """Load scores from localStorage (JSON file).
        
        If the file doesn't exist, initializes an empty scoreboard.
        """
        if not os.path.exists(self.storage_path):
            self.scores = []
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                scores_data = json.load(f)
            
            self.scores = [Score.from_dict(data) for data in scores_data]
        except (IOError, json.JSONDecodeError, ValueError) as e:
            raise IOError(f"Failed to load scores from {self.storage_path}: {e}")
    
    def clear_all(self) -> None:
        """Clear all scores from the scoreboard."""
        self.scores = []
        self.save_to_localStorage()
    
    def get_all_scores(self) -> List[Score]:
        """Get all scores.
        
        Returns:
            List of all Score objects
        """
        return self.scores.copy()
