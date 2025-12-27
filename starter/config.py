"""Configuration for Sudoku game."""

from typing import Dict, Tuple

# Difficulty levels with clue count ranges (min, max)
DIFFICULTY_LEVELS: Dict[str, Tuple[int, int]] = {
    'easy': (40, 45),        # 40-45 prefilled cells
    'medium': (30, 35),      # 30-35 prefilled cells
    'hard': (25, 28),        # 25-28 prefilled cells
    'expert': (17, 20),      # 17-20 prefilled cells
}

# Default difficulty level
DEFAULT_DIFFICULTY = 'medium'

# Sudoku board configuration
BOARD_SIZE = 9
BOX_SIZE = 3

# Game configuration
MAX_HINTS = 3
SECONDS_PER_HINT = 300  # 5 minutes between hints
