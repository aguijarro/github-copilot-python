# Keyboard Shortcuts & Navigation Guide

## Quick Reference

### Sudoku Board Navigation
Use **arrow keys** to navigate the puzzle board:
- **↑** = Move up
- **↓** = Move down  
- **←** = Move left
- **→** = Move right
- **1-9** = Enter number (auto-advances to next cell)
- **Backspace** or **Delete** = Clear cell

### General Navigation
- **Tab** = Move to next button/input
- **Shift + Tab** = Move to previous button/input
- **Enter** = Activate button or submit form

### Modal Dialogs
- **Enter** = Submit (on form fields)
- **Tab** = Focus next button
- **Esc** = Not implemented (use close button)

---

## Detailed Keyboard Navigation

### Starting a Game

1. **Press Tab** to navigate to game controls
2. **Arrow Left/Right** in difficulty select (if desired)
3. **Press Enter** on "New Game" button
4. **Tab** to sudoku board - first cell gets focus

### Playing the Game

#### Basic Movement
```
Arrow Keys navigate the 9×9 grid:

    ↑
  ← → 
    ↓

Examples:
- Press ↑ from Row 5 → goes to Row 4 (same column)
- Press ↑ from Row 1 → goes to Row 9 (wraps to bottom)
- Press → from Column 9 → goes to Column 1 (wraps to left)
```

#### Entering Numbers
```
Press any number 1-9:
- Number appears in current cell
- Cursor automatically moves to next cell (right)
- Validate happens in real-time (shows conflicts/errors)

Example: 
1. Focus cell [Row 1, Col 1]
2. Press "5" → cell shows 5, focus moves to [Row 1, Col 2]
3. Press "3" → cell shows 3, focus moves to [Row 1, Col 3]
```

#### Clearing Cells
```
Press Backspace or Delete:
- Clears the current cell value
- Cursor stays on same cell
- Validation updates immediately

Example:
1. Cell contains "7"
2. Press Backspace
3. Cell is now empty
```

### Completing the Puzzle

1. **Navigate cells** until puzzle is solved
2. **Press "Check Solution"** button (Tab to it)
3. **If correct**, congratulations modal appears
   - **Tab** to "Play Again" button
   - **Press Enter** to start new game
4. **If incorrect**, error message shows
   - Can continue playing

### Saving Your Score

1. After solving puzzle, congratulations modal appears
2. **Press Tab** to "Play Again" button (if shown)
   - OR modals auto-transitions to name input
3. **Name input modal** appears
   - Type your name (1-20 characters)
   - **Tab** to "Save Score" button
   - **Press Enter** to submit
4. **Success** - score saved to leaderboard

### Using Hint

1. **Tab** to "Hint" button
2. **Press Enter**
3. Random empty cell is filled
4. Hint counter decreases (aria-live announces)

### Checking Work

#### Check Button
```
1. Tab to "Check" button
2. Press Enter
3. Cells with errors show orange background
4. Fix and check again
```

#### Check Solution Button  
```
1. Tab to "Check Solution" button
2. Press Enter
3. If all cells correct → Congratulations!
4. If any wrong → Shows which cells are incorrect
```

---

## Screen Reader Specific Navigation

### Navigating with Screen Reader

When using NVDA, JAWS, or other screen readers:

```
1. Open game page
2. Screen reader announces: "Sudoku Game, main landmark"

3. Press Tab to navigate:
   - Theme toggle button
   - Difficulty select
   - Game buttons (New Game, Check, Check Solution)
   - Sudoku board cells
   - Hint button
   - Scoreboard table

4. Each cell announces:
   - "Row 1, Column 1" (aria-label)
   - "Empty" (if no value)
   - Or the number (if filled)

5. Error messages announced via aria-live:
   - "Conflict detected in Row 2, Column 5"
   - "Two cells with same number"

6. Form fields:
   - "Player name input, maximum 20 characters"
   - Error: "Name must be 1-20 characters"
```

### ARIA Live Updates

The following regions use aria-live and are announced:

| Region | Type | Content |
|--------|------|---------|
| Hint counter | polite | "Hints: 3" |
| Error messages | assertive | Validation errors |
| Status message | assertive | Check results |
| Modal alerts | assertive | Congratulations/errors |

---

## Common Tasks - Step by Step

### Task: Solve Puzzle with Only Keyboard

```
1. Page loads → Tab key focuses first interactive element
2. Tab to "New Game" → Press Enter → Board appears
3. Focus goes to first cell [1,1]
4. Type "5" → Moves to [1,2]
5. Type "3" → Moves to [1,3]
... continue until puzzle solved ...
6. Tab to "Check Solution" → Press Enter
7. If correct → "Play Again" button appears
8. Tab to it → Press Enter → New puzzle starts
```

### Task: Save Your Score

```
1. After solving → Congratulations modal
2. Wait for auto-transition OR
3. Tab to "Play Again" → Modal transitions to name input
4. Type name: "Alice" (auto-focuses name input)
5. Tab to "Save Score" button (button enabled automatically)
6. Press Enter → Score saved
7. Scoreboard updates with your name and time
```

### Task: Navigate to Difficult Cell

```
1. Need to go to Row 8, Column 4
2. Currently at Row 3, Column 7
3. Press ↓ 5 times (Row 8)
4. Press ← 3 times (Column 4)
5. Now focused on [Row 8, Column 4]
6. Type number → cell updates
```

### Task: Clear Entire Row

```
1. Focus first cell of row: [Row 5, Column 1]
2. For each cell:
   - Press Backspace
   - Press →
3. Row is now empty
```

---

## Accessibility Features by Component

### Sudoku Board
- ✅ Arrow key navigation
- ✅ Auto-advance on entry
- ✅ Backspace/Delete support
- ✅ aria-label on each cell
- ✅ Clear focus indicator
- ✅ Real-time validation

### Buttons
- ✅ Full keyboard focus (Tab/Shift+Tab)
- ✅ Descriptive aria-labels
- ✅ Enter key activation
- ✅ Visible focus state
- ✅ Hover and active states

### Form Inputs
- ✅ Label associated (via <label> or aria-label)
- ✅ Error messages linked (aria-describedby)
- ✅ Real-time validation feedback
- ✅ Disabled state when invalid
- ✅ Tab order maintained

### Modals
- ✅ Tab navigates buttons
- ✅ Close button available
- ✅ Focus trapped appropriately
- ✅ Announced to screen readers
- ✅ Enter submits forms

---

## Browser DevTools Testing

### Chrome DevTools
1. F12 → Open DevTools
2. Accessibility panel:
   - Shows ARIA tree
   - Check element roles
   - Verify labels
3. Lighthouse:
   - Run accessibility audit
   - Shows accessibility score
   - Lists issues (if any)

### Firefox Inspector
1. F12 → Open Inspector
2. Inspector → Accessibility tab
3. Shows:
   - Accessibility tree
   - Roles and labels
   - Keyboard shortcuts
   - Color contrast info

### Testing Keyboard
1. Unplug mouse (or disable trackpad)
2. Use only Tab, Enter, arrow keys
3. Verify all features work
4. Check focus is always visible
5. No keyboard traps

---

## Tips for Keyboard Users

1. **Always visible focus**: Look for blue outline or highlight
2. **Use Tab wisely**: Skip unnecessary elements with Shift+Tab
3. **Arrow keys on board**: Much faster than Tab for navigation
4. **Number + Space/Enter**: Enter numbers quickly
5. **Check frequently**: Use Check button to verify progress
6. **Use Hint sparingly**: Limited hints available

---

## Known Limitations

- Close modal with Escape key: Not implemented (use close button)
- Keyboard-only mouse alternatives: Covered by standard navigation
- Voice control: Should work with browser's built-in voice features
- Custom shortcuts: Not yet customizable (use browser extensions)

---

## Testing Checklist

- [ ] All buttons reachable via Tab
- [ ] Arrow keys navigate sudoku board
- [ ] Numbers 1-9 enter in cells
- [ ] Backspace clears cells
- [ ] Enter submits forms
- [ ] Focus always visible
- [ ] Error messages announced
- [ ] No keyboard traps (can always Tab away)
- [ ] Screen reader reads all content
- [ ] Tab order is logical

---

## Additional Resources

- [WAI-ARIA Keyboard Patterns](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Keyboard Accessibility](https://webaim.org/articles/keyboard/)
- [Keyboard Focus Indicators](https://www.a11yproject.com/posts/2021-01-28-an-introduction-to-visible-focus-indicators/)

---

## Questions?

If you encounter keyboard navigation issues:
1. Check browser console for JavaScript errors (F12)
2. Verify number lock is on (for numpad)
3. Try different browser (Chrome, Firefox, Safari, Edge)
4. Test with screen reader (NVDA on Windows)
5. Report issues with:
   - Browser name and version
   - Screen reader used (if any)
   - Specific action that failed
   - Error messages (F12 console)
