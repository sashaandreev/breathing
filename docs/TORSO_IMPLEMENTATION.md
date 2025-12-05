# Torso Graphic Implementation Guide

## Overview

This document provides the implementation details for the torso graphic used in the breathing guide screen. The implementation uses SVG with CSS animations for smooth, synchronized pulsing effects.

## SVG Structure

### Complete SVG Markup

```html
<svg id="torso-graphic" viewBox="0 0 100 200" preserveAspectRatio="xMidYMid meet" class="torso-container">
    <!-- Torso Outline (for NOSTRILS/MOUTH/ALL subtle pulse) -->
    <path id="torso-outline" 
          d="M 30 10 Q 30 5 50 5 Q 70 5 70 10 L 70 30 Q 70 35 65 40 L 65 90 Q 65 95 50 95 Q 35 95 35 90 L 35 40 Q 30 35 30 30 Z" 
          fill="none" 
          stroke="#E0E0E0" 
          stroke-width="2"
          class="torso-outline"/>
    
    <!-- Separation Line (subtle horizontal divider) -->
    <line id="separation-line" 
          x1="25" y1="90" x2="75" y2="90" 
          stroke="#E0E0E0" 
          stroke-width="1" 
          stroke-opacity="0.5"
          stroke-dasharray="2,2"/>
    
    <!-- Chest Area (upper torso, lungs) -->
    <rect id="chest-area" 
          x="25" y="15" 
          width="50" height="75" 
          rx="5" 
          class="breath-target chest-target"
          fill="transparent"/>
    
    <!-- Abdomen Area (lower torso, diaphragm) -->
    <rect id="abdomen-area" 
          x="25" y="90" 
          width="50" height="100" 
          rx="5" 
          class="breath-target abdomen-target"
          fill="transparent"/>
</svg>
```

### Improvements Over Original Suggestion

1. **Anatomically Shaped Outline**: Added a curved path that better represents a torso shape
2. **Rounded Corners**: Added `rx="5"` to rectangles for softer appearance
3. **Subtle Separation Line**: Used dashed line with reduced opacity for less visual weight
4. **Responsive Design**: `preserveAspectRatio` ensures proper scaling on all devices
5. **Better Positioning**: Adjusted coordinates for better proportions

## CSS Implementation

### Base Styles

```css
/* Container */
.torso-container {
    width: 100%;
    max-width: 200px;
    height: auto;
    margin: 0 auto;
}

/* Torso Outline Base */
#torso-outline {
    fill: none;
    stroke: #E0E0E0;
    stroke-width: 2;
    transition: stroke 0.3s ease-in-out, stroke-width 0.3s ease-in-out;
}

/* Target Areas Base State */
.breath-target {
    fill: transparent;
    opacity: 0;
    transition: opacity 0.4s ease-in-out, fill 0.4s ease-in-out, filter 0.4s ease-in-out;
    pointer-events: none; /* Don't interfere with interactions */
}

/* Chest Area Specific */
.chest-target {
    /* Slightly different styling if needed */
}

/* Abdomen Area Specific */
.abdomen-target {
    /* Slightly different styling if needed */
}
```

### Pulse States

```css
/* --- Active Pulse State (ABDOMEN/CHEST during Inhale) --- */
.is-pulsing {
    fill: rgba(255, 215, 0, 0.5); /* #FFD700 with 50% opacity */
    opacity: 0.5;
    filter: drop-shadow(0 0 6px rgba(255, 215, 0, 0.6));
    /* Animation synchronized with breathing phase duration */
    animation: none; /* Controlled by JavaScript for precise timing */
}

/* --- Subtle Pulse State (NOSTRILS/MOUTH/ALL during Inhale) --- */
.is-pulsing-subtle {
    stroke: #00A38D; /* Match balloon color */
    stroke-width: 3;
    opacity: 1;
    filter: drop-shadow(0 0 4px rgba(0, 163, 141, 0.4));
    transition: stroke 0.3s ease-in-out, stroke-width 0.3s ease-in-out;
}

/* --- Exhale Dimming (removed by JavaScript) --- */
/* Simply removing .is-pulsing or .is-pulsing-subtle classes
   triggers the transition back to base state */
```

### Keyframe Animation (Optional - for subtle continuous pulse)

```css
/* Optional: Gentle continuous pulse during hold phases */
@keyframes gentle-pulse {
    0%, 100% { 
        opacity: 0.5; 
        filter: drop-shadow(0 0 4px rgba(255, 215, 0, 0.4));
    }
    50% { 
        opacity: 0.7; 
        filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.6));
    }
}

/* Apply only during hold phases if desired */
.is-holding {
    animation: gentle-pulse 2s ease-in-out infinite;
}
```

## JavaScript Integration

### Class Management

```javascript
class TorsoPulseController {
    constructor(torsoElement) {
        this.torso = document.getElementById('torso-graphic');
        this.chestArea = document.getElementById('chest-area');
        this.abdomenArea = document.getElementById('abdomen-area');
        this.torsoOutline = document.getElementById('torso-outline');
        this.currentTarget = null;
    }

    // Start pulse based on breath_origin
    startPulse(breathOrigin, phase) {
        this.clearPulse(); // Remove any existing pulse
        
        if (phase === 'inhale') {
            switch(breathOrigin) {
                case 'ABDOMEN':
                    this.abdomenArea.classList.add('is-pulsing');
                    this.currentTarget = this.abdomenArea;
                    break;
                case 'CHEST':
                    this.chestArea.classList.add('is-pulsing');
                    this.currentTarget = this.chestArea;
                    break;
                case 'NOSTRILS':
                case 'MOUTH':
                case 'ALL':
                    this.torsoOutline.classList.add('is-pulsing-subtle');
                    this.currentTarget = this.torsoOutline;
                    break;
            }
        }
    }

    // End pulse (exhale phase)
    endPulse() {
        if (this.currentTarget) {
            this.currentTarget.classList.remove('is-pulsing', 'is-pulsing-subtle');
            this.currentTarget = null;
        }
    }

    // Clear all pulse states
    clearPulse() {
        this.chestArea.classList.remove('is-pulsing');
        this.abdomenArea.classList.remove('is-pulsing');
        this.torsoOutline.classList.remove('is-pulsing-subtle');
        this.currentTarget = null;
    }

    // Update opacity during animation (for smooth transitions)
    updateOpacity(opacity) {
        if (this.currentTarget && this.currentTarget.classList.contains('is-pulsing')) {
            this.currentTarget.style.opacity = opacity;
        }
    }
}
```

### Integration with Breathing Engine

```javascript
// In your breathing guide JavaScript
const torsoPulse = new TorsoPulseController();

function updateBreathingPhase(phase, breathOrigin, elapsedTime, phaseDuration) {
    switch(phase) {
        case 'inhale':
            torsoPulse.startPulse(breathOrigin, 'inhale');
            // Animate opacity from 0 to 0.5 over inhale duration
            const inhaleProgress = elapsedTime / phaseDuration;
            torsoPulse.updateOpacity(0.5 * inhaleProgress);
            break;
            
        case 'exhale':
            torsoPulse.endPulse();
            // Opacity transitions back to 0 via CSS
            break;
            
        case 'hold':
        case 'hold_end':
            // Maintain current state
            break;
    }
}
```

## Improvements Over Original Suggestion

### 1. **Color Alignment**
- Changed from `rgba(255, 230, 150, 0.5)` to `rgba(255, 215, 0, 0.5)` to match design spec (#FFD700)
- Ensures consistency with design document

### 2. **Animation Control**
- Removed independent CSS animation (`gentle-pulse 1.2s infinite`)
- Animation now controlled by JavaScript to sync with actual breathing phases
- Opacity changes match balloon animation timing exactly

### 3. **Better SVG Path**
- Added actual path data for torso outline (curved, anatomical shape)
- More visually appealing than simple rectangle

### 4. **Responsive Design**
- Added `preserveAspectRatio` for proper scaling
- Max-width constraint for mobile optimization
- Better viewBox proportions

### 5. **Separation Line Enhancement**
- Dashed line with reduced opacity for subtlety
- Less visual weight, doesn't compete with pulse effects

### 6. **Performance**
- `pointer-events: none` on target areas prevents interaction issues
- Smooth CSS transitions instead of JavaScript-driven animations where possible

### 7. **Code Organization**
- Separate controller class for better maintainability
- Clear methods for each state transition
- Easy to extend for future features

## Mobile Optimization

```css
/* Mobile-specific adjustments */
@media (max-width: 420px) {
    .torso-container {
        max-width: 150px;
    }
    
    #torso-graphic {
        width: 100%;
        height: auto;
    }
}
```

## Testing Checklist

- [ ] Pulse activates correctly for ABDOMEN breath_origin
- [ ] Pulse activates correctly for CHEST breath_origin
- [ ] Subtle pulse activates for NOSTRILS/MOUTH/ALL
- [ ] Opacity transitions smoothly during inhale (0 → 0.5)
- [ ] Opacity transitions smoothly during exhale (0.5 → 0)
- [ ] Pulse synchronizes with balloon animation
- [ ] No visual glitches when switching between phases
- [ ] Works correctly on mobile devices (375px - 420px width)
- [ ] Separation line is visible but not distracting
- [ ] Colors match design specifications

## Alternative: CSS-Only Approach

If you prefer a simpler CSS-only approach without JavaScript class management:

```css
/* Use CSS custom properties for dynamic control */
.breath-target {
    --pulse-opacity: 0;
    --pulse-color: rgba(255, 215, 0, 0.5);
    fill: var(--pulse-color);
    opacity: var(--pulse-opacity);
    transition: opacity 0.4s ease-in-out;
}

/* JavaScript updates CSS variables */
element.style.setProperty('--pulse-opacity', '0.5');
```

This approach gives more fine-grained control but requires more JavaScript.

## Recommendation

**Use the JavaScript class-based approach** because:
1. Cleaner separation of concerns
2. Easier to debug and maintain
3. Better performance (CSS handles transitions)
4. More flexible for future enhancements
5. Aligns with existing JavaScript architecture

The suggested implementation is excellent, and these improvements enhance it for production use.

