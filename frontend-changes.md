# Frontend Changes: Dark/Light Theme Toggle

## Files Modified

### `frontend/index.html`
- Added `data-theme="dark"` attribute to `<body>` for CSS theme selection
- Added a theme toggle `<button>` with inline SVG sun and moon icons, positioned inside `.main-content`
- Bumped cache-busting versions for `style.css` (v14) and `script.js` (v13)

### `frontend/style.css`
- **Light theme CSS variables**: Added `[data-theme="light"]` selector with a full set of overridden variables (background, surface, text, border, source-link colors, code block backgrounds)
- **New CSS variables**: Extracted hardcoded `rgba()` values into variables (`--code-bg`, `--source-link-bg`, `--source-link-color`, etc.) so both themes can override them
- **Toggle button styles**: `.theme-toggle` — fixed position top-right, circular button with hover/focus/active states, smooth scale and rotation transitions
- **Icon visibility**: Sun icon shows in dark mode, moon icon shows in light mode, controlled via `[data-theme] .sun-icon / .moon-icon` display rules
- **Smooth transitions**: Added `transition` on `body`, `.sidebar`, and source links for background-color, color, and border-color changes (0.3s ease)

### `frontend/script.js`
- **`initTheme()`**: Reads saved theme from `localStorage` on page load, applies it to `data-theme`, and sets the correct `aria-label`
- **`toggleTheme()`**: Switches between `dark` and `light`, updates `data-theme`, persists to `localStorage`, and updates aria-label
- **`updateThemeAriaLabel()`**: Keeps the button's `aria-label` in sync (e.g., "Switch to light theme" when currently dark)
- Added `themeToggle` to DOM element references and wired up the click listener in `setupEventListeners()`

## Design Decisions
- **Icon approach**: Sun icon (dark mode = "click for light") and moon icon (light mode = "click for dark") using inline SVGs matching the existing send-button style
- **Persistence**: `localStorage` stores the preference so it survives page reloads
- **Accessibility**: `aria-label` updates dynamically, button is keyboard-focusable with visible focus ring, meets contrast requirements in both themes
- **No breaking changes**: All existing functionality is preserved; dark theme remains the default
