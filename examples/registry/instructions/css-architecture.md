# CSS Architecture and Design Systems Expert

Use this expert when tasks require establishing CSS methodology, building or maintaining design systems, implementing responsive layouts, managing theming (dark mode, brand variants), and choosing between utility-first (Tailwind), modular (CSS Modules), or custom property-driven styling approaches.

## When to use this expert
- The task involves choosing a CSS strategy for a new project or migrating an existing codebase to a scalable approach.
- A design token system must be created to enforce consistent spacing, color, and typography across the application.
- Responsive layout, dark mode, or multi-brand theming must be implemented or restructured.
- CSS specificity conflicts, deeply nested selectors, or inconsistent breakpoints are causing maintenance pain.

## Execution behavior

1. Define design tokens as CSS custom properties on `:root` (or a data attribute scope for theming). Tokens cover color palette, spacing scale (4px base), font sizes, border radii, shadows, and z-index layers.
2. Choose the primary styling method. Prefer Tailwind CSS for utility-first rapid development; use CSS Modules when component-scoped class names are needed without a utility framework; use plain CSS custom properties plus BEM for teams that prefer semantic class names.
3. Establish a responsive breakpoint system using mobile-first `min-width` media queries. Define breakpoints as design tokens or Tailwind config values: `sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`. Never mix `min-width` and `max-width` queries in the same project.
4. Implement dark mode using a `data-theme` attribute on `<html>` or the `prefers-color-scheme` media query. Map semantic color tokens (`--color-bg-primary`, `--color-text-primary`) to different values per theme rather than overriding individual component styles.
5. When using Tailwind, extract repeated utility combinations into component classes with `@apply` only when a pattern appears in three or more places. Prefer React component abstraction over `@apply` for most reuse.
6. Establish spacing and sizing using the token scale exclusively. Replace magic numbers (`margin: 13px`) with scale values (`margin: var(--space-3)` or Tailwind `m-3`). Enforce this via linting.
7. Audit selector specificity. Keep selectors at one class deep when possible. Avoid nesting beyond three levels. Never use `!important` except for third-party style overrides documented with a comment explaining why.
8. Document the design system tokens and component patterns in a living style guide or Storybook instance so that contributors can discover and reuse existing patterns.

## Decision tree
- If the team values speed and small bundle with purged CSS -> Tailwind CSS with the project's `tailwind.config` defining the design tokens.
- If component-level style isolation is critical and the project avoids global CSS -> CSS Modules (`.module.css`) with composes for shared tokens.
- If the project must support multiple brand themes at runtime -> CSS custom properties scoped to a `data-theme` attribute, with a JavaScript toggle.
- If responsive layout is needed -> mobile-first `min-width` breakpoints; use container queries for components that must adapt to their parent rather than the viewport.
- If a component has more than five conditional Tailwind classes -> extract it into a `cn()` / `clsx()` helper call for readability; do not resort to inline ternary chains.
- If a third-party library injects styles that conflict -> scope the override in a dedicated file with minimal `!important` use, documented with the library name and issue.

## Anti-patterns
- NEVER use inline `style` attributes for layout, spacing, or colors. They bypass the design system, cannot be themed, and have the highest specificity.
- NEVER chain `!important` declarations to win specificity battles. Refactor selectors to lower specificity or restructure the cascade instead.
- NEVER use magic numbers for spacing, font sizes, or colors. Every value must trace back to a design token.
- NEVER mix `min-width` and `max-width` media queries in the same project. Pick one direction (mobile-first with `min-width` is standard) and be consistent.
- NEVER nest selectors more than three levels deep (e.g., `.page .section .card .header .title`). Flat selectors are easier to override and understand.
- NEVER duplicate breakpoint values across files. Define them once in a shared config (Tailwind config, CSS custom properties, or Sass variables).

## Common mistakes
- Defining colors as raw hex values scattered across component files instead of centralizing them as design tokens, making theme changes a search-and-replace nightmare.
- Using `max-width` breakpoints to "undo" desktop styles for mobile, resulting in convoluted overrides instead of progressively enhancing from a mobile base.
- Over-relying on `@apply` in Tailwind to recreate traditional CSS class hierarchies, losing the utility-first benefit and increasing bundle size.
- Forgetting to include a `font-family` fallback stack, so when a custom font fails to load, the browser renders in an unexpected serif or monospace default.
- Setting `z-index: 9999` instead of using a defined z-index scale, causing layer conflicts that are nearly impossible to debug.
- Ignoring the `:focus-visible` pseudo-class and either showing focus rings on every click or removing them entirely, both of which are accessibility failures.

## Output contract
- All color, spacing, typography, and shadow values must reference design tokens, not raw literals.
- Responsive styles must follow a mobile-first `min-width` breakpoint progression.
- Dark mode and theming must be implemented via CSS custom properties scoped to a togglable attribute or media query.
- Selector nesting must not exceed three levels, and `!important` must not appear except in documented third-party overrides.
- Tailwind projects must have a configured `tailwind.config` with the project's design tokens (colors, spacing, fonts) as the single source of truth.
- A living style guide or Storybook must document the available tokens and component patterns.
- Every component must be visually tested at the smallest (`sm`) and largest (`xl`) breakpoints at minimum.

## Composability hints
- Before this expert -> use a **Design/UX Review** process to establish the visual language, spacing scale, and color palette before codifying tokens.
- After this expert -> use the **React Expert** or **Next.js Expert** to integrate the styling system into component architecture.
- After this expert -> use the **Accessibility Expert** to verify color contrast ratios (4.5:1 AA), focus indicators, and reduced-motion preferences.
- Related -> the **React Native Expert** for translating design tokens into `StyleSheet.create` values for mobile.
- Related -> the **State Management Expert** when theme preference must be persisted and synchronized across components.
