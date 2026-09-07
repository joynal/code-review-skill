# CSS, Less, and Sass Review Guide

Inspect the browser support policy, Browserslist/build configuration, design tokens, and whether syntax is native CSS or transformed by Sass, Less, or PostCSS.

## Cascade and isolation

- Trace computed styles through specificity, source order, inheritance, cascade layers, and `!important` before proposing a fix.
- Normal unlayered author styles outrank normal layered author styles. Important declarations reverse layer ordering; moving rules into `@layer` can change behavior. See [cascade layers](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@layer).
- `:where()` contributes zero specificity; it does not increase the strength of an override.
- `!important`, repeated values, and selector depth are not automatic defects. Report the concrete override, theme inconsistency, or maintainability requirement that fails.
- Follow established tokens and variable scope. Custom properties are runtime values and cannot generally replace literals in media-query conditions.

## Layout and accessibility

- Check long content, localization, text zoom, narrow screens, orientation changes, and empty/error states for clipping and overflow.
- Flex/grid children may need an explicit minimum size adjustment to shrink as intended. Verify the containing block for positioned elements.
- Check stacking contexts and overflow clipping for menus, dialogs, sticky elements, and focus rings. A large `z-index` does not escape an ancestor stacking context.
- Verify visible keyboard focus, contrast, reduced-motion behavior, and touch targets against the project's accessibility requirements.
- Hiding content visually is not necessarily hiding it from assistive technology; `display: none` and a visually-hidden utility have different semantics.
- Mobile-first and desktop-first media queries are both valid. Evaluate the resulting layout.

## Animation and performance

Identify the actual animated properties and affected elements. Layout/paint work can matter, but `transition: all`, shadows, or deep selectors are not inherently blocking defects.

Prefer measured evidence for rendering-cost claims. Transforms and opacity often avoid layout work, but are not guarantees of free compositing. Check that substitutions preserve geometry, hit areas, and readability. `contain` can change clipping/layout behavior; `will-change` can consume resources when kept widely enabled.

## Browser and preprocessor compatibility

- Check exact feature support for the project's target browsers, including native nesting, `:has()`, container queries, viewport units, and layers. Use feature detection/fallbacks only where required.
- A fallback must not stack with the supported behavior unintentionally; adding both gap and unconditional margins can double spacing.
- Inspect compiled selectors for Sass/Less nesting and `@extend`; native nesting is not identical to preprocessor interpolation or concatenation.
- Dart Sass deprecated `@import` and global built-in functions in 1.80.0. For affected migrations, use `@use`/`@forward` and namespaced functions, verifying output and dependency compatibility. See [Sass migration guidance](https://sass-lang.com/documentation/breaking-changes/import/).

## Focused examples

### Moving an override into a layer changes its priority

Assume a browser supporting cascade layers, a button with `class="button"`, and a product requirement for a blue button. The snippets are alternatives.

```css
/* Bad: the unlayered red declaration outranks the normal layered one. */
.button { color: red; }
@layer app {
  .button { color: blue; }
}

/* Good: both rules participate in the explicit vendor-to-app layer order. */
@layer vendor, app;
@layer vendor {
  .button { color: red; }
}
@layer app {
  .button { color: blue; }
}
```

**Why:** the bad button remains red even though the blue declaration appears later. The good button is blue because `app` comes after `vendor` for normal declarations. This assumes control over where vendor styles are loaded; adding a layer declaration alone does not move existing unlayered CSS into it. Important declarations use different precedence. See [cascade layers](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@layer).

### Removing keyboard focus without a visible replacement

Assume an otherwise unstyled button and a white page background.

```css
/* Bad: a keyboard user loses the browser's visible focus indicator. */
.button:focus {
  outline: none;
}

/* Good: retain focus feedback with a visible indicator. */
.button:focus {
  outline: 3px solid #174ea6;
  outline-offset: 3px;
}
```

**Why:** tabbing to the bad button no longer shows which control will activate. The good rule provides a visible outline. Removing the native outline is acceptable when another adequate indicator already exists; inspect computed styles and clipping before reporting it. Verify contrast against the actual theme and use `:focus-visible` when appropriate for the supported browsers and interaction design. See [focus styling](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:focus).

## Validation

Use existing style checks and inspect the rendered affected states in supported browsers when possible. Report which viewport/state was actually checked. Do not add legacy-browser polyfills, IE configuration, or a new CSS toolchain without an applicable support requirement.
