// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let gameId = null;
let lockedCells = new Set();
let conflictCells = new Set();
let validationTimeout = null;
let gameStartTime = null;
let currentDifficulty = 'medium';
let hintsUsed = 0;
let checkHighlightTimeout = null;
let checkConflictCells = new Set();
let timerInterval = null;
let elapsedSeconds = 0;
let lastGameStats = null; // Store game stats for score submission


function getCurrentBoard() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

async function validateBoard() {
  const board = getCurrentBoard();
  
  try {
    const res = await fetch('/validate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    
    const data = await res.json();
    
    // Clear previous conflict highlighting
    conflictCells.forEach(cellKey => {
      const [row, col] = cellKey.split('-').map(Number);
      const idx = row * SIZE + col;
      const boardDiv = document.getElementById('sudoku-board');
      const inputs = boardDiv.getElementsByTagName('input');
      const inp = inputs[idx];
      if (inp) {
        inp.classList.remove('conflict');
      }
    });
    conflictCells.clear();
    
    // Add new conflict highlighting
    if (data.has_conflicts && data.conflicts) {
      data.conflicts.forEach(([row, col]) => {
        const cellKey = `${row}-${col}`;
        conflictCells.add(cellKey);
        const idx = row * SIZE + col;
        const boardDiv = document.getElementById('sudoku-board');
        const inputs = boardDiv.getElementsByTagName('input');
        const inp = inputs[idx];
        if (inp && !inp.disabled) {
          inp.classList.add('conflict');
        }
      });
    }
  } catch (error) {
    console.error('Validation error:', error);
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.setAttribute('aria-label', `Row ${i + 1}, Column ${j + 1}`);
      
      // Determine 3x3 block colors (alternating)
      const blockRow = Math.floor(i / 3);
      const blockCol = Math.floor(j / 3);
      if ((blockRow + blockCol) % 2 === 0) {
        input.classList.add('cell-light');
      } else {
        input.classList.add('cell-dark');
      }
      
      input.addEventListener('input', (e) => {
        // Prevent input if cell is locked
        const cellKey = `${i}-${j}`;
        if (lockedCells.has(cellKey)) {
          e.preventDefault();
          e.target.value = puzzle[i][j];
          return;
        }
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        
        // Auto-move to next cell if value entered
        if (val) {
          const nextCol = j + 1;
          if (nextCol < SIZE) {
            const nextInput = document.querySelector(`input[data-row="${i}"][data-col="${nextCol}"]`);
            if (nextInput) nextInput.focus();
          }
        }
        
        validateCell(i, j);
      });
      
      // Add arrow key navigation
      input.addEventListener('keydown', (e) => {
        const row = parseInt(e.target.dataset.row);
        const col = parseInt(e.target.dataset.col);
        
        let nextRow = row;
        let nextCol = col;
        
        switch(e.key) {
          case 'ArrowUp':
            e.preventDefault();
            nextRow = (row - 1 + SIZE) % SIZE;
            break;
          case 'ArrowDown':
            e.preventDefault();
            nextRow = (row + 1) % SIZE;
            break;
          case 'ArrowLeft':
            e.preventDefault();
            nextCol = (col - 1 + SIZE) % SIZE;
            break;
          case 'ArrowRight':
            e.preventDefault();
            nextCol = (col + 1) % SIZE;
            break;
          case 'Backspace':
          case 'Delete':
            e.preventDefault();
            e.target.value = '';
            validateCell(row, col);
            return;
          default:
            return;
        }
        
        const nextInput = document.querySelector(`input[data-row="${nextRow}"][data-col="${nextCol}"]`);
        if (nextInput) nextInput.focus();
      });
      
      // Validate board after input (debounced)
      clearTimeout(validationTimeout);
      validationTimeout = setTimeout(validateBoard, 200);
      
      boardDiv.appendChild(input);
    }
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  lockedCells.clear();
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
        lockedCells.add(`${i}-${j}`);
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty-select').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  gameId = data.game_id;
  currentDifficulty = difficulty;
  gameStartTime = Date.now();
  hintsUsed = 0;
  updateHintCounter();
  document.getElementById('hint-btn').disabled = false;
  startTimer();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  closeCongratulationsModal();
}

async function checkComplete() {
  const board = getCurrentBoard();
  
  try {
    const res = await fetch('/check-complete', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    
    const data = await res.json();
    
    if (data.is_complete) {
      // Stop timer when puzzle is complete
      stopTimer();
      // Disable hint button when puzzle is complete
      document.getElementById('hint-btn').disabled = true;
      showCongratulationsModal();
    }
  } catch (error) {
    console.error('Completion check error:', error);
  }
}

function updateHintCounter() {
  document.getElementById('hint-counter').textContent = `Hints: ${hintsUsed}`;
}

function updateTimer() {
  const minutes = Math.floor(elapsedSeconds / 60);
  const seconds = elapsedSeconds % 60;
  const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  document.getElementById('timer').textContent = `⏱️ ${timeString}`;
}

function startTimer() {
  elapsedSeconds = 0;
  updateTimer();
  
  // Clear any existing timer
  if (timerInterval) {
    clearInterval(timerInterval);
  }
  
  // Start new timer
  timerInterval = setInterval(() => {
    elapsedSeconds++;
    updateTimer();
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

async function checkConflicts() {
  const board = getCurrentBoard();
  
  try {
    const res = await fetch('/validate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    
    const data = await res.json();
    
    // Clear any previous highlight timeout
    if (checkHighlightTimeout) {
      clearTimeout(checkHighlightTimeout);
    }
    
    // Clear previous check highlights
    checkConflictCells.forEach(cellKey => {
      const [row, col] = cellKey.split('-').map(Number);
      const idx = row * SIZE + col;
      const boardDiv = document.getElementById('sudoku-board');
      const inputs = boardDiv.getElementsByTagName('input');
      const inp = inputs[idx];
      if (inp) {
        inp.classList.remove('check-conflict');
      }
    });
    checkConflictCells.clear();
    
    // Add new check highlights
    if (data.has_conflicts && data.conflicts) {
      data.conflicts.forEach(([row, col]) => {
        const cellKey = `${row}-${col}`;
        checkConflictCells.add(cellKey);
        const idx = row * SIZE + col;
        const boardDiv = document.getElementById('sudoku-board');
        const inputs = boardDiv.getElementsByTagName('input');
        const inp = inputs[idx];
        if (inp) {
          inp.classList.add('check-conflict');
        }
      });
      
      // Display message
      const conflictCount = data.conflicts.length;
      document.getElementById('message').innerText = `Found ${conflictCount} conflict(s)!`;
      document.getElementById('message').style.color = '#ff9800';
      
      // Clear highlights after 2 seconds
      checkHighlightTimeout = setTimeout(() => {
        checkConflictCells.forEach(cellKey => {
          const [row, col] = cellKey.split('-').map(Number);
          const idx = row * SIZE + col;
          const boardDiv = document.getElementById('sudoku-board');
          const inputs = boardDiv.getElementsByTagName('input');
          const inp = inputs[idx];
          if (inp) {
            inp.classList.remove('check-conflict');
          }
        });
        checkConflictCells.clear();
        document.getElementById('message').innerText = '';
      }, 2000);
    } else {
      document.getElementById('message').innerText = 'No conflicts found! Keep going! ✓';
      document.getElementById('message').style.color = '#388e3c';
    }
  } catch (error) {
    console.error('Check error:', error);
    document.getElementById('message').innerText = 'Error checking board';
    document.getElementById('message').style.color = '#d32f2f';
  }
}

function showCongratulationsModal() {
  const modal = document.getElementById('congratulations-modal');
  
  // Calculate elapsed time
  const elapsedMs = Date.now() - gameStartTime;
  const minutes = Math.floor(elapsedMs / 60000);
  const seconds = Math.floor((elapsedMs % 60000) / 1000);
  const totalSeconds = minutes * 60 + seconds;
  const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  
  // Store game stats for score submission
  lastGameStats = {
    time: totalSeconds,
    difficulty: currentDifficulty,
    hints: hintsUsed
  };
  
  // Update modal content with game stats
  document.getElementById('modal-time').textContent = timeString;
  document.getElementById('modal-difficulty').textContent = 
    currentDifficulty.charAt(0).toUpperCase() + currentDifficulty.slice(1);
  document.getElementById('modal-hints').textContent = hintsUsed.toString();
  
  modal.classList.add('show');
  
  // Show name input modal after a delay
  setTimeout(() => {
    showNameInputModal();
  }, 500);
}

function closeCongratulationsModal() {
  const modal = document.getElementById('congratulations-modal');
  modal.classList.remove('show');
}

function showNameInputModal() {
  const modal = document.getElementById('name-input-modal');
  const input = document.getElementById('player-name-input');
  const errorDiv = document.getElementById('name-error');
  const submitBtn = document.getElementById('submit-name-btn');
  
  // Clear previous input and error
  input.value = '';
  errorDiv.textContent = '';
  submitBtn.disabled = true;
  input.focus();
  
  modal.classList.add('show');
}

function closeNameInputModal() {
  const modal = document.getElementById('name-input-modal');
  const input = document.getElementById('player-name-input');
  const errorDiv = document.getElementById('name-error');
  
  modal.classList.remove('show');
  input.value = '';
  errorDiv.textContent = '';
}

function validatePlayerName(name) {
  const trimmed = name.trim();
  
  if (!trimmed) {
    return { valid: false, error: 'Name cannot be empty' };
  }
  
  if (trimmed.length < 1) {
    return { valid: false, error: 'Name must be at least 1 character' };
  }
  
  if (trimmed.length > 20) {
    return { valid: false, error: 'Name must be 20 characters or less' };
  }
  
  return { valid: true };
}

async function submitScore(playerName) {
  if (!lastGameStats) {
    console.error('Game stats not available');
    return;
  }
  
  const trimmedName = playerName.trim();
  
  // Validate name
  const validation = validatePlayerName(trimmedName);
  if (!validation.valid) {
    const errorDiv = document.getElementById('name-error');
    errorDiv.textContent = validation.error;
    return;
  }
  
  try {
    const response = await fetch('/api/scores', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: trimmedName,
        time: lastGameStats.time,
        difficulty: lastGameStats.difficulty,
        hints: lastGameStats.hints
      })
    });
    
    if (!response.ok) {
      const data = await response.json();
      const errorDiv = document.getElementById('name-error');
      errorDiv.textContent = data.error || 'Failed to save score';
      return;
    }
    
    // Success - close modal and refresh scoreboard
    closeNameInputModal();
    loadScoreboard();
    
    // Show success message briefly
    const msgElement = document.getElementById('message');
    msgElement.textContent = `✓ Score saved for ${trimmedName}!`;
    msgElement.style.color = '#388e3c';
    setTimeout(() => {
      msgElement.textContent = '';
    }, 3000);
    
  } catch (error) {
    console.error('Error submitting score:', error);
    const errorDiv = document.getElementById('name-error');
    errorDiv.textContent = 'Error saving score. Please try again.';
  }
}


async function getHint() {
  const board = getCurrentBoard();
  
  try {
    const res = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board, game_id: gameId})
    });
    
    const data = await res.json();
    
    if (res.ok) {
      // Fill the cell with the hint value
      const boardDiv = document.getElementById('sudoku-board');
      const inputs = boardDiv.getElementsByTagName('input');
      const idx = data.row * SIZE + data.col;
      const inp = inputs[idx];
      
      if (inp) {
        inp.value = data.value;
        inp.disabled = true;
        inp.className = 'sudoku-cell prefilled';
        lockedCells.add(`${data.row}-${data.col}`);
        
        // Update hints counter
        hintsUsed = data.hints_used;
        updateHintCounter();
        
        // Clear any conflicts on this cell
        inp.classList.remove('conflict');
        
        document.getElementById('message').innerText = `Hint revealed! (${data.hints_used} hints used)`;
      }
    } else {
      const errorMsg = data.error || 'Failed to get hint';
      document.getElementById('message').innerText = errorMsg;
      document.getElementById('message').style.color = '#d32f2f';
    }
  } catch (error) {
    console.error('Hint error:', error);
    document.getElementById('message').innerText = 'Error getting hint';
    document.getElementById('message').style.color = '#d32f2f';
  }
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board, game_id: gameId})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    checkComplete();
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons and modal events
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-btn').addEventListener('click', checkConflicts);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-btn').addEventListener('click', getHint);
  
  // Modal event listeners
  const modal = document.getElementById('congratulations-modal');
  const closeBtn = document.querySelector('.close-btn');
  const playAgainBtn = document.getElementById('play-again-btn');
  
  closeBtn.addEventListener('click', () => {
    closeCongratulationsModal();
  });
  
  playAgainBtn.addEventListener('click', () => {
    closeCongratulationsModal();
    closeNameInputModal();
    newGame();
  });
  
  window.addEventListener('click', (event) => {
    if (event.target === modal) {
      closeCongratulationsModal();
    }
  });
  
  // Name input modal listeners
  const nameInputModal = document.getElementById('name-input-modal');
  const nameCloseBtn = nameInputModal.querySelector('.close-btn');
  const cancelNameBtn = document.getElementById('cancel-name-btn');
  const submitNameBtn = document.getElementById('submit-name-btn');
  const playerNameInput = document.getElementById('player-name-input');
  
  nameCloseBtn.addEventListener('click', () => {
    closeNameInputModal();
  });
  
  cancelNameBtn.addEventListener('click', () => {
    closeNameInputModal();
  });
  
  submitNameBtn.addEventListener('click', () => {
    const playerName = playerNameInput.value;
    submitScore(playerName);
  });
  
  playerNameInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
      const playerName = playerNameInput.value;
      submitScore(playerName);
    }
  });

  // Enable/disable submit button based on name validation
  playerNameInput.addEventListener('input', (event) => {
    const validation = validatePlayerName(event.target.value);
    submitNameBtn.disabled = !validation.valid;
    submitNameBtn.setAttribute('aria-disabled', !validation.valid);
  });
  
  playerNameInput.addEventListener('change', (event) => {
    const validation = validatePlayerName(event.target.value);
    if (!validation.valid) {
      document.getElementById('name-error').textContent = validation.error;
      document.getElementById('name-error').setAttribute('role', 'alert');
    } else {
      document.getElementById('name-error').textContent = '';
    }
  });
  
  window.addEventListener('click', (event) => {
    if (event.target === nameInputModal) {
      closeNameInputModal();
    }
  });
  
  // Load scoreboard on page load
  loadScoreboard();
  
  // initialize
  newGame();
});

/**
 * Load and display scores from localStorage (data/scores.json)
 */
function loadScoreboard() {
  fetch('/api/scores')
    .then(response => response.json())
    .then(scores => {
      displayScoreboard(scores);
    })
    .catch(error => {
      console.log('Scores not yet available:', error);
      // Show empty state if file doesn't exist yet
      displayScoreboard([]);
    });
}

/**
 * Display scores in the scoreboard table
 * @param {Array} scores - Array of score objects from API
 */
function displayScoreboard(scores) {
  const tbody = document.getElementById('scoreboard-body');
  
  if (!scores || scores.length === 0) {
    // Show empty message
    tbody.innerHTML = '<tr class="empty-message"><td colspan="5">No scores yet. Complete a puzzle to see scores here!</td></tr>';
    return;
  }
  
  // Clear existing rows
  tbody.innerHTML = '';
  
  // Add top 10 scores
  const topScores = scores.slice(0, 10);
  topScores.forEach((score, index) => {
    const row = document.createElement('tr');
    row.className = index % 2 === 0 ? 'even-row' : 'odd-row';
    
    const formattedTime = formatTime(score.time);
    const difficultyClass = `difficulty-${score.difficulty}`;
    
    row.innerHTML = `
      <td class="rank-cell">${index + 1}</td>
      <td class="name-cell">${escapeHtml(score.name)}</td>
      <td class="time-cell">${formattedTime}</td>
      <td class="difficulty-cell ${difficultyClass}">${score.difficulty}</td>
      <td class="hints-cell">${score.hints}</td>
    `;
    
    tbody.appendChild(row);
  });
}

/**
 * Format time in seconds to MM:SS format
 * @param {number} seconds - Time in seconds
 * @returns {string} Formatted time string
 */
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

/**
 * Escape HTML special characters to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, char => map[char]);
}

// Theme Toggle Functionality
function initializeThemeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  if (!themeToggle) return;

  // Update button text based on current theme
  const updateThemeButton = () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    themeToggle.querySelector('.theme-icon').textContent = isDark ? '☀️' : '🌙';
  };

  // Toggle theme on button click
  themeToggle.addEventListener('click', () => {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    
    if (isDark) {
      html.removeAttribute('data-theme');
      localStorage.setItem('sudoku-theme', 'light');
    } else {
      html.setAttribute('data-theme', 'dark');
      localStorage.setItem('sudoku-theme', 'dark');
    }
    
    updateThemeButton();
  });

  // Initial button state
  updateThemeButton();

  // Listen for system preference changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    const savedTheme = localStorage.getItem('sudoku-theme');
    // Only update if no saved preference
    if (!savedTheme) {
      if (e.matches) {
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }
      updateThemeButton();
    }
  });
}

// Initialize theme toggle when DOM is ready
document.addEventListener('DOMContentLoaded', initializeThemeToggle);
