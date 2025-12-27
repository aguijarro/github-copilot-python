## Scoreboard Usage Guide

The `Scoreboard` class provides functionality to manage and persist player scores for the Sudoku game.

### Overview

The Scoreboard manages a collection of `Score` objects, each containing:
- **name**: Player name (string)
- **time**: Time taken to complete puzzle in seconds (int)
- **difficulty**: Difficulty level - one of: 'easy', 'medium', 'hard', 'expert' (string)
- **hints**: Number of hints used (int)
- **date**: Timestamp when score was recorded (datetime)

### Basic Usage

```python
from models.scoreboard import Scoreboard

# Initialize Scoreboard (loads existing scores from file if available)
scoreboard = Scoreboard(storage_path='data/scores.json')

# Add a new score
score = scoreboard.add_score(
    name='Alice',
    time=300,  # 5 minutes
    difficulty='medium',
    hints=2
)

# Get top 10 scores (sorted by fastest time)
top_scores = scoreboard.get_top_10()
for score in top_scores:
    print(f"{score.name}: {score.time}s on {score.difficulty}")
```

### Available Methods

#### `add_score(name, time, difficulty, hints) -> Score`
Adds a new score to the scoreboard and automatically saves to file.

**Parameters:**
- `name` (str): Player name (required, non-empty)
- `time` (int): Time in seconds (required, non-negative)
- `difficulty` (str): One of 'easy', 'medium', 'hard', 'expert'
- `hints` (int): Number of hints used (required, non-negative)

**Returns:** The created `Score` object

**Raises:** `ValueError` if any parameter is invalid

#### `get_top_10() -> List[Score]`
Returns top 10 scores sorted by fastest time.

```python
top_10 = scoreboard.get_top_10()  # Returns up to 10 scores
```

#### `get_scores_by_difficulty(difficulty) -> List[Score]`
Get all scores for a specific difficulty level.

```python
easy_scores = scoreboard.get_scores_by_difficulty('easy')
```

#### `get_top_10_by_difficulty(difficulty) -> List[Score]`
Get top 10 scores for a specific difficulty level.

```python
hard_top_10 = scoreboard.get_top_10_by_difficulty('hard')
```

#### `get_all_scores() -> List[Score]`
Get all recorded scores.

```python
all_scores = scoreboard.get_all_scores()
```

#### `save_to_localStorage() -> None`
Manually save all scores to JSON file. (Called automatically by `add_score()`)

#### `load_from_localStorage() -> None`
Manually load scores from JSON file. (Called automatically on initialization)

#### `clear_all() -> None`
Clear all scores from the scoreboard and save to file.

```python
scoreboard.clear_all()  # Clears all records
```

### Score Serialization

Scores are automatically converted to/from JSON format for persistence:

```python
# Convert Score to dictionary
score_dict = score.to_dict()
# {'name': 'Alice', 'time': 300, 'difficulty': 'medium', 'hints': 2, 'date': '2025-12-27T10:30:00'}

# Create Score from dictionary
score = Score.from_dict(score_dict)
```

### File Storage

- Scores are stored as JSON in `data/scores.json` by default
- Directory is automatically created if it doesn't exist
- Each score includes ISO format timestamp for precise tracking
- File is updated automatically whenever scores are added or modified

### Error Handling

```python
from models.scoreboard import Scoreboard

try:
    scoreboard = Scoreboard(storage_path='data/scores.json')
    score = scoreboard.add_score('Alice', 300, 'medium', 2)
except ValueError as e:
    print(f"Invalid score data: {e}")
except IOError as e:
    print(f"File I/O error: {e}")
```

### Integration with Flask

To integrate Scoreboard with the game service:

```python
from models.scoreboard import Scoreboard
from services.game_service import GameService

# Create scoreboard instance
scoreboard = Scoreboard()

# Add score after game completion
score = scoreboard.add_score(
    name=player_name,
    time=elapsed_time,
    difficulty=game_difficulty,
    hints=hints_used
)
```

### Testing

The module includes comprehensive tests covering:
- Score validation
- Serialization/deserialization
- Adding and retrieving scores
- Difficulty filtering
- File persistence
- Edge cases and error handling

Run tests with:
```bash
pytest tests/test_scoreboard.py -v
```
