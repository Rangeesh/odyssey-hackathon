# Dark Mode Feature

## Overview

LYRA now includes a beautiful dark mode that's easy on the eyes during nighttime use or in low-light environments. The theme preference is saved locally and persists across sessions.

## How to Use

### Toggle Dark Mode

1. Look for the **theme toggle button** in the top-right corner of the header
2. Click the button to switch between light and dark modes
3. The icon changes:
   - 🌙 (Moon) = Light mode is active, click to enable dark mode
   - ☀️ (Sun) = Dark mode is active, click to enable light mode

### Theme Persistence

Your theme preference is automatically saved in your browser's local storage. When you return to the app, it will remember your choice.

## Visual Design

### Light Mode (Default)
- **Background**: Purple gradient (#667eea to #764ba2)
- **Cards**: White backgrounds
- **Text**: Dark gray (#333)
- **Accents**: Purple (#667eea)

### Dark Mode
- **Background**: Dark blue gradient (#1a1a2e to #16213e)
- **Cards**: Deep blue backgrounds (#0f3460)
- **Text**: Light gray (#e0e0e0)
- **Accents**: Light purple (#7b68ee)

## Features

### Smooth Transitions
- All color changes animate smoothly (0.3s transition)
- Theme toggle button rotates 360° when clicked
- Hover effects work in both themes

### Comprehensive Theming
Every element is themed:
- ✅ Header and footer
- ✅ Main content area
- ✅ Input fields and buttons
- ✅ Job cards
- ✅ Progress bars
- ✅ Status badges
- ✅ Info boxes and messages
- ✅ Video containers

### Accessibility
- High contrast ratios in both modes
- Clear visual feedback on interactions
- Aria label for screen readers
- Keyboard accessible (can tab to button)

## Technical Details

### CSS Variables

The theme system uses CSS custom properties (variables) for easy maintenance:

```css
:root {
    --bg-gradient-start: #667eea;
    --bg-gradient-end: #764ba2;
    --text-primary: #333;
    /* ... more variables */
}

[data-theme="dark"] {
    --bg-gradient-start: #1a1a2e;
    --bg-gradient-end: #16213e;
    --text-primary: #e0e0e0;
    /* ... dark mode overrides */
}
```

### JavaScript Implementation

```javascript
// Theme is stored in localStorage
localStorage.setItem('theme', 'dark');

// Applied via data attribute
document.documentElement.setAttribute('data-theme', 'dark');

// Automatically loads on page load
const savedTheme = localStorage.getItem('theme') || 'light';
```

### Browser Support

Works in all modern browsers:
- ✅ Chrome 49+
- ✅ Firefox 31+
- ✅ Safari 9.1+
- ✅ Edge 15+

Requires:
- CSS Custom Properties support
- localStorage API
- ES6 JavaScript

## Customization

### Change Colors

Edit `/backend/video_generator/static/video_generator/css/style.css`:

```css
[data-theme="dark"] {
    --bg-gradient-start: #your-color;
    --bg-gradient-end: #your-color;
    --accent-color: #your-color;
    /* ... etc */
}
```

### Change Transition Speed

Modify the transition duration:

```css
body {
    transition: background 0.5s ease, color 0.5s ease;
}
```

### Add System Preference Detection

To automatically match system dark mode:

```javascript
// Add to app.js
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const savedTheme = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light');
```

## Color Palette

### Light Mode
| Element | Color | Hex |
|---------|-------|-----|
| Background Start | Purple | #667eea |
| Background End | Purple | #764ba2 |
| Text Primary | Dark Gray | #333333 |
| Text Secondary | Gray | #666666 |
| Card Background | White | #ffffff |
| Accent | Purple | #667eea |

### Dark Mode
| Element | Color | Hex |
|---------|-------|-----|
| Background Start | Dark Blue | #1a1a2e |
| Background End | Navy | #16213e |
| Text Primary | Light Gray | #e0e0e0 |
| Text Secondary | Gray | #b0b0b0 |
| Card Background | Deep Blue | #0f3460 |
| Accent | Light Purple | #7b68ee |

## User Feedback

The theme toggle provides multiple forms of feedback:
1. **Visual**: Icon changes (moon ↔ sun)
2. **Animation**: 360° rotation on click
3. **Hover**: Scale up to 110%
4. **Active**: Scale down to 95%
5. **Immediate**: Theme changes instantly

## Best Practices

### For Users
1. **Choose based on environment**:
   - Light mode: Bright rooms, daytime
   - Dark mode: Dark rooms, nighttime, reduced eye strain
2. **Try both**: See which you prefer
3. **Theme persists**: No need to toggle every visit

### For Developers
1. **Always use CSS variables**: Don't hardcode colors
2. **Test both themes**: Ensure readability in both
3. **Maintain contrast**: Keep text readable
4. **Smooth transitions**: Use consistent timing
5. **Save preference**: Use localStorage

## Troubleshooting

### Theme Not Saving
- Check browser localStorage is enabled
- Clear browser cache and try again
- Check browser console for errors

### Colors Look Wrong
- Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Clear browser cache
- Check CSS file loaded correctly

### Button Not Working
- Check JavaScript console for errors
- Verify app.js is loaded
- Check browser JavaScript is enabled

## Future Enhancements

Potential improvements:
- Auto-switch based on time of day
- Multiple theme options (blue, green, etc.)
- Custom theme builder
- Sync theme across devices
- Animated theme transitions
- High contrast mode for accessibility

## Examples

### Light Mode Screenshot
```
┌─────────────────────────────────────────┐
│ 🎵 LYRA - LYRics Animated          🌙  │
│ AI-Powered Music Video Generator        │
├─────────────────────────────────────────┤
│ [Purple gradient background]            │
│ [White content cards]                   │
│ [Dark text on light background]         │
└─────────────────────────────────────────┘
```

### Dark Mode Screenshot
```
┌─────────────────────────────────────────┐
│ 🎵 LYRA - LYRics Animated          ☀️  │
│ AI-Powered Music Video Generator        │
├─────────────────────────────────────────┤
│ [Dark blue gradient background]         │
│ [Deep blue content cards]               │
│ [Light text on dark background]         │
└─────────────────────────────────────────┘
```

## Performance

- **No performance impact**: CSS-only theming
- **Instant switching**: No page reload needed
- **Lightweight**: ~2KB additional CSS
- **Efficient**: Uses CSS variables (hardware accelerated)

---

**Version**: 1.1.0  
**Added**: February 6, 2026  
**Status**: Production Ready ✅
