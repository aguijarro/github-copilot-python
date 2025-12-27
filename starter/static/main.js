// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let gameId = null;
let lockedCells = new Set();
let conflictCells = new Set();
let validationTimeout = null;

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
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
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
        
        // Validate board after input (debounced)
        clearTimeout(validationTimeout);
        validationTimeout = setTimeout(validateBoard, 200);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
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
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
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
      showCongratulationsModal();
    }
  } catch (error) {
    console.error('Completion check error:', error);
  }
}

function showCongratulationsModal() {
  const modal = document.getElementById('congratulations-modal');
  const messageEl = document.getElementById('modal-message');
  const timeEl = document.getElementById('modal-time');
  
  messageEl.textContent = 'You have successfully completed the puzzle!';
  timeEl.textContent = 'Great job! You solved it!';
  
  modal.classList.add('show');
}

function closeCongratulationsModal() {
  const modal = document.getElementById('congratulations-modal');
  modal.classList.remove('show');
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
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  
  // Modal event listeners
  const modal = document.getElementById('congratulations-modal');
  const closeBtn = document.querySelector('.close-btn');
  const playAgainBtn = document.getElementById('play-again-btn');
  
  closeBtn.addEventListener('click', () => {
    closeCongratulationsModal();
  });
  
  playAgainBtn.addEventListener('click', () => {
    closeCongratulationsModal();
    newGame();
  });
  
  window.addEventListener('click', (event) => {
    if (event.target === modal) {
      closeCongratulationsModal();
    }
  });
  
  // initialize
  newGame();
});