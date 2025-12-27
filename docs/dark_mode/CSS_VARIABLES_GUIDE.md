## CSS Theme Variables Reference

### Overview
The Sudoku game now uses CSS custom properties (variables) for all colors, making it easy to implement light/dark themes or customize the appearance.

### CSS Variables Defined in `:root`

#### Background & Layout Colors
- `--bg-color: #f4f4f4` - Main page background
- `--modal-bg: #fff` - Modal and panel backgrounds
- `--highlight-color: #e0f7fa` - Highlight/focus color

#### Text & Border Colors
- `--text-color: #333` - Primary text color
- `--border-color: #bbb` - Border and divider colors
- `--modal-border: #e0e0e0` - Modal border color

#### Button & Interactive Colors
- `--button-bg: #1976d2` - Primary button background
- `--button-hover-bg: #1565c0` - Button hover state
- `--primary-color: #1976d2` - Primary accent color

#### Game Element Colors
- `--cell-bg: #fafafa` - Sudoku cell background
- `--cell-prefilled-bg: #e0e0e0` - Pre-filled cell background
- `--warning-color: #ff9800` - Hint button color

#### Status Colors
- `--success-color: #388e3c` - Success/positive feedback
- `--danger-color: #d32f2f` - Error/danger feedback

#### Table Styling
- `--table-header-bg: #1976d2` - Table header background
- `--table-header-text: #fff` - Table header text color
- `--table-odd-row-bg: #f5f5f5` - Odd row background
- `--table-even-row-bg: #ffffff` - Even row background
- `--table-hover-bg: #e3f2fd` - Table row hover state

### Current Light Mode Defaults

```css
:root {
    --bg-color: #f4f4f4;
    --text-color: #333;
    --cell-bg: #fafafa;
    --cell-prefilled-bg: #e0e0e0;
    --border-color: #bbb;
    --button-bg: #1976d2;
    --button-hover-bg: #1565c0;
    --highlight-color: #e0f7fa;
    --primary-color: #1976d2;
    --success-color: #388e3c;
    --danger-color: #d32f2f;
    --warning-color: #ff9800;
    --modal-bg: #fff;
    --modal-border: #e0e0e0;
    --table-header-bg: #1976d2;
    --table-header-text: #fff;
    --table-odd-row-bg: #f5f5f5;
    --table-even-row-bg: #ffffff;
    --table-hover-bg: #e3f2fd;
}
```

### How to Implement Dark Mode

Add a dark mode selector to override the variables:

```css
/* Dark Mode */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-color: #1e1e1e;
        --text-color: #e0e0e0;
        --cell-bg: #2d2d2d;
        --cell-prefilled-bg: #3d3d3d;
        --border-color: #555;
        --button-bg: #0d47a1;
        --button-hover-bg: #1565c0;
        --highlight-color: #1a3a52;
        --primary-color: #2196f3;
        --success-color: #66bb6a;
        --danger-color: #ef5350;
        --warning-color: #ffa726;
        --modal-bg: #2d2d2d;
        --modal-border: #444;
        --table-header-bg: #1565c0;
        --table-header-text: #e0e0e0;
        --table-odd-row-bg: #252525;
        --table-even-row-bg: #2d2d2d;
        --table-hover-bg: #3d3d3d;
    }
}
```

### How to Implement Custom Theme

You can also override variables with a custom class:

```css
/* Custom Brand Theme */
.custom-theme {
    --primary-color: #e74c3c;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --danger-color: #c0392b;
    --button-bg: #e74c3c;
    --button-hover-bg: #c0392b;
}
```

Then apply the class to the HTML element:
```html
<html class="custom-theme">
```

### Usage in CSS

All colors are now referenced using `var()` function:

```css
/* Example: Using variables in your CSS */
.my-element {
    background-color: var(--modal-bg);
    color: var(--text-color);
    border: 1px solid var(--border-color);
}

.my-button {
    background: var(--button-bg);
}

.my-button:hover {
    background: var(--button-hover-bg);
}
```

### Benefits

✓ **Consistent Theming**: Change all colors in one place
✓ **Easy Dark Mode**: Override variables with `prefers-color-scheme`
✓ **Customizable**: Users or admins can customize colors
✓ **Maintainable**: No hardcoded colors scattered throughout CSS
✓ **Flexible**: Support multiple themes without duplicate CSS
✓ **Performant**: No JavaScript theme switching needed

### Fallbacks

All variables have been refactored into the CSS, so fallback colors are not needed. However, older browsers (IE 10 and earlier) won't support CSS variables. To maintain compatibility, you could add fallback colors:

```css
.element {
    background: #fff; /* fallback for old browsers */
    background: var(--modal-bg);
}
```

However, CSS variables are supported in all modern browsers (Chrome 49+, Firefox 31+, Safari 9.1+, Edge 15+).

### Files Modified
- [static/styles.css](static/styles.css) - Added CSS variables and refactored all colors

### Testing
- ✓ All 165 tests passing
- ✓ Light mode fully functional
- ✓ Ready for dark mode implementation
- ✓ No breaking changes
