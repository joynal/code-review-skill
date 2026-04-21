# CSS / Less / Sass Review Guide

A guide to reviewing CSS and preprocessor code, covering performance, maintainability, responsive design, and browser compatibility.

## CSS variables vs hardcoding

### Scenarios where variables should be used

```css
/* ❌ Hard-coded - difficult to maintain */
.button {
  background: #3b82f6;
  border-radius: 8px;
}
.card {
  border: 1px solid #3b82f6;
  border-radius: 8px;
}

/* ✅ Use CSS variables */
:root {
  --color-primary: #3b82f6;
  --radius-md: 8px;
}
.button {
  background: var(--color-primary);
  border-radius: var(--radius-md);
}
.card {
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
}
```

### Variable naming convention

```css
/* Recommended variable classification */
:root {
/* color */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-text: #1f2937;
  --color-text-muted: #6b7280;
  --color-bg: #ffffff;
  --color-border: #e5e7eb;

/* spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

/* font */
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-weight-normal: 400;
  --font-weight-bold: 700;

/* rounded corners */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

/* shadow */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);

/* Transition */
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
}
```

/* ✅ Component-level variables - reduce global pollution */

```css
/* ✅ Component-level variables - reduce global pollution */
.card {
  --card-padding: var(--spacing-md);
  --card-radius: var(--radius-md);

  padding: var(--card-padding);
  border-radius: var(--card-radius);
}

/* ⚠️ Avoid frequently using JS to dynamically modify variables - affecting performance */
```

### Review Checklist

- [ ] Do color values ​​use variables?
- [ ] Does the spacing come from the design system?
- [ ] Are duplicate values ​​extracted as variables?
- [ ] Are variable names semantic?

---

## !important usage specifications

### When can it be used?

```css
/* ✅ Tool class - clearly needs to be covered */
.hidden { display: none !important; }
.sr-only { position: absolute !important; }

/* ✅ Override third-party library styles (when source code cannot be modified) */
.third-party-modal {
  z-index: 9999 !important;
}

/* ✅Print style */
@media print {
  .no-print { display: none !important; }
}
```

### When is prohibited?

```css
/* ❌ Solve specificity issues - selectors should be refactored */
.button {
background: blue !important; /* Why do we need !important? */
}

/* ❌ Overwrite your own style */
.card { padding: 20px; }
.card { padding: 30px !important; } /* Directly modify the original rule */

/* ❌ in component style */
.my-component .title {
font-size: 24px !important; /* Destroy component encapsulation */
}
```

### Alternatives

```css
/* Problem: Need to override the style of .btn */

/* ❌ Use !important */
.my-btn {
  background: red !important;
}

/* ✅ Use :where() to reduce the specificity of overridden styles */
button.my-btn {
  background: red;
}

/* ✅ Use more specific selectors */
.container .my-btn {
  background: red;
}

/* ✅ Use :where() to reduce the specificity of overridden styles */
:where(.btn) {
background: blue; /* Specificity is 0 */
}
.my-btn {
background: red; /* can be covered normally */
}
```

🔴 [blocking] "Found 15 !important, please explain the necessity of each one"

```markdown
🔴 [blocking] "Found 15 !important, please explain the necessity of each one"
🟡 [important] "This !important can be solved by adjusting the selector specificity"
💡 [suggestion] "Consider using CSS Layers (@layer) to manage style priority"
```

---

### 🔴 High-risk performance issues

### 🔴 High-risk performance issues

#### 1. `transition: all` problem

```css
/* ❌ Performance killer - the browser checks all animatable properties */
.button {
  transition: all 0.3s ease;
}

/* ✅ Explicitly specify attributes */
.button {
  transition: background-color 0.3s ease, transform 0.3s ease;
}

/* ✅ Use variables when using multiple attributes */
.button {
  --transition-duration: 0.3s;
  transition:
    background-color var(--transition-duration) ease,
    box-shadow var(--transition-duration) ease,
    transform var(--transition-duration) ease;
}
```

#### 2. box-shadow animation

```css
/* ❌ Trigger redraw every frame - seriously affects performance */
.card {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: box-shadow 0.3s ease;
}
.card:hover {
  box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

/* ✅ Use pseudo-element + opacity */
.card {
  position: relative;
}
.card::after {
  content: '';
  position: absolute;
  inset: 0;
  box-shadow: 0 8px 16px rgba(0,0,0,0.2);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  border-radius: inherit;
}
.card:hover::after {
  opacity: 1;
}
```

#### 3. Attributes that trigger layout (Reflow)

```css
/* ❌ Animating these properties will trigger layout recalculation */
.bad-animation {
  transition: width 0.3s, height 0.3s, top 0.3s, left 0.3s, margin 0.3s;
}

/* ✅ Only animate transform and opacity (only trigger compositing) */
.good-animation {
  transition: transform 0.3s, opacity 0.3s;
}

/* Use translate instead of top/left for displacement */
.move {
  transform: translateX(100px);  /* ✅ */
  /* left: 100px; */             /* ❌ */
}

/* Use scale instead of width/height for scaling */
.grow {
  transform: scale(1.1);  /* ✅ */
  /* width: 110%; */      /* ❌ */
}
```

### 🟡 Moderate performance issues

#### Complex selector

```css
/* ❌ Too deep nesting - selector matching is slow */
.page .container .content .article .section .paragraph span {
  color: red;
}

/* ✅ Flatten */
.article-text {
  color: red;
}

/* ❌ wildcard selector */
[class*="icon-"] { display: inline; } /* Attribute selector is slow */
[class*="icon-"] { display: inline; } /* Attribute selector is slow */

/* ✅ Restricted range */
.icon-box * { box-sizing: border-box; }
```

#### Lots of shadows and filters

```css
/* ⚠️ Complex shadows affect rendering performance */
.heavy-shadow {
  box-shadow:
    0 1px 2px rgba(0,0,0,0.1),
    0 2px 4px rgba(0,0,0,0.1),
    0 4px 8px rgba(0,0,0,0.1),
    0 8px 16px rgba(0,0,0,0.1),
0 16px 32px rgba(0,0,0,0.1); /* 5 layers of shadow */
}

/* ⚠️ Filter consumes GPU */
.blur-heavy {
  filter: blur(20px) brightness(1.2) contrast(1.1);
backdrop-filter: blur(10px); /* consumes more performance */
}
```

### Performance optimization suggestions

```css
/* Use will-change to prompt the browser (use with caution) */
.animated-element {
  will-change: transform, opacity;
}

/* Remove will-change after animation completes */
.animated-element.idle {
  will-change: auto;
}

/* Use contain to limit the redraw range */
.card {
contain: layout paint; /* Tell the browser that internal changes will not affect the outside */
}
```

### Review Checklist

- [ ] Do you want to use `transition: all`?
- [ ] Whether to animate width/height/top/left?
- [ ] Is the selector nested more than 3 levels deep?
- [ ] Is the selector nested more than 3 levels deep?
- [ ] Is there any unnecessary `will-change`?

---

## Responsive design checkpoints

### Mobile First principle

```css
/* ✅ Mobile First - basic styles for mobile */
.container {
  padding: 16px;
  display: flex;
  flex-direction: column;
}

/* Gradually enhance */
@media (min-width: 768px) {
  .container {
    padding: 24px;
    flex-direction: row;
  }
}

@media (min-width: 1024px) {
  .container {
    padding: 32px;
    max-width: 1200px;
    margin: 0 auto;
  }
}

/* ❌ Desktop First - more styles need to be covered */
.container {
  max-width: 1200px;
  padding: 32px;
  flex-direction: row;
}

@media (max-width: 1023px) {
  .container {
    padding: 24px;
  }
}

@media (max-width: 767px) {
  .container {
    padding: 16px;
    flex-direction: column;
    max-width: none;
  }
}
```

### Breakpoint suggestions

```css
/* Recommended breakpoints (based on content rather than device) */
:root {
--breakpoint-sm: 640px; /* Large mobile phones */
--breakpoint-md: 768px; /* Tablet vertical screen */
--breakpoint-lg: 1024px; /* Tablet landscape/small notebook */
--breakpoint-xl: 1280px; /* desktop */
--breakpoint-2xl: 1536px; /* Large desktop */
}

/* Usage example */
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
```

### Responsive Review Checklist

- [ ] Mobile First?
- [ ] Are breakpoints based on content breakpoints rather than device?
- [ ] Do you want to avoid overlapping breakpoints?
- [ ] Does the text use relative units (rem/em)?
- [ ] Is the touch target large enough (≥44px)?
- [ ] Have you tested switching between horizontal and vertical screens?

### FAQ

```css
/* ❌ fixed width */
.container {
  width: 1200px;
}

/* ✅ Maximum width + elasticity */
.container {
  width: 100%;
  max-width: 1200px;
  padding-inline: 16px;
}

/* ❌ Fixed height text container */
.text-box {
height: 100px; /* text may overflow */
}

/* ✅ Minimum height */
.text-box {
  min-height: 100px;
}

padding: 4px 8px; /* too small to click */
.small-button {
padding: 4px 8px; /* too small to click */
}

/* ✅ Enough touch area */
.touch-button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px;
}
```

---

## Browser compatibility

### Features to check

| Features | Compatibility | Recommendations |
|------|--------|------|
| CSS Grid | Modern browsers ✅ | IE requires Autoprefixer + testing |
| Flexbox | Widely supported ✅ | Older versions require prefix |
| CSS Variables | Modern browsers ✅ | IE not supported, need to fall back |
| `gap` (flexbox) | Newer ⚠️ | Safari 14.1+ |
| `:has()` | Newer ⚠️ | Firefox 121+ |
| `container queries` | Newer ⚠️ | Post-2023 browsers |
| `@layer` | Newer ⚠️ | Check target browser |

### Fallback strategy

```css
/* CSS variable fallback */
.button {
background: #3b82f6; /* fallback value */
background: var(--color-primary); /* modern browsers */
}

/* Flexbox gap rollback */
.flex-container {
  display: flex;
  gap: 16px;
}
/* Fallback to old browsers */
.flex-container > * + * {
  margin-left: 16px;
}

/* Grid rollback */
.grid {
  display: flex;
  flex-wrap: wrap;
}
@supports (display: grid) {
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}
```

### Autoprefixer configuration

```javascript
// postcss.config.js
module.exports = {
  plugins: [
    require('autoprefixer')({
grid: 'autoplace', // Enable Grid prefix (IE support)
grid: 'autoplace', // Enable Grid prefix (IE support)
flexbox: 'no-2009', // only use modern flexbox syntax
    }),
  ],
};

// package.json
{
  "browserslist": [
    "> 1%",
    "last 2 versions",
    "not dead",
"not ie 11" // According to project requirements
  ]
}
```

### Review Checklist

- [ ] Have you checked [Can I Use](https://caniuse.com)?
- [ ] Is there a rollback plan for the new features?
- [ ] Is Autoprefixer configured?
- [ ] Does browserslist meet project requirements?
- [ ] Testing in target browsers?

---


### Nesting depth

```scss
/* ❌ Too deep nesting - the compiled selector is too long */
.page {
  .container {
    .content {
      .article {
        .title {
color: red; // Compile to .page .container .content .article .title
        }
      }
    }
  }
}

/* ✅ Up to 3 layers */
.article {
  &__title {
    color: red;
  }

  &__content {
    p { margin-bottom: 1em; }
  }
}
```

### Mixin vs Extend vs Variable

```scss
/* Variable - for a single value */
$primary-color: #3b82f6;

/* Mixin - for configurable code blocks */
@mixin button-variant($bg, $text) {
  background: $bg;
  color: $text;
  &:hover {
    background: darken($bg, 10%);
  }
}

/* Extend - for sharing the same style (use with caution) */
%visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}

.sr-only {
  @extend %visually-hidden;
}

/* ⚠️ @extend’s question */
// May produce unexpected selector combinations
// Cannot be used in @media
// Prefer using mixins
```

### Review Checklist

- [ ] Is there more than 3 levels of nesting?
- [ ] Is the mixin too complex?
- [ ] Is the mixin too complex?
- [ ] Is the compiled CSS a reasonable size?

---

## Quick Review Checklist

### 🔴 Must be fixed

```markdown
□ transition: all
□ animation width/height/top/left/margin
□ A lot of !important
□ Hardcoded color/spacing repeated >3 times
□ Selector nesting >4 levels
```

### 🟡 Suggested fixes

```markdown
□ Lack of responsive processing
□ Use Desktop First
□ Complex box-shadow is animated
□ Lack of browser compatibility fallback
□ CSS variable scope is too large
```

### 🟢 Optimization suggestions

```markdown
□ You can use CSS Grid to simplify layout
□ You can use @layer to manage priorities
□ You can use @layer to manage priorities
□ You can add contain to optimize performance
```

---

## Tool recommendation

| Tools | Purpose |
|------|------|
| [PurgeCSS](https://purgecss.com/) | Remove unused CSS |
| [PurgeCSS](https://purgecss.com/) | Remove unused CSS |
| [Autoprefixer](https://autoprefixer.github.io/) | Automatically add prefixes |
| [CSS Stats](https://cssstats.com/) | Analyze CSS statistics |
| [Can I Use](https://caniuse.com/) | Browser compatibility query |

---

## Reference resources

- [CSS Performance Optimization - MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Performance/CSS)
- [What a CSS Code Review Might Look Like - CSS-Tricks](https://css-tricks.com/what-a-css-code-review-might-look-like/)
- [How to Animate Box-Shadow - Tobias Ahlin](https://tobiasahlin.com/blog/how-to-animate-box-shadow/)
- [Media Query Fundamentals - MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Media_queries)
- [Autoprefixer - GitHub](https://github.com/postcss/autoprefixer)
