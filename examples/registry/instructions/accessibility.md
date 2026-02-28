# Web Accessibility (WCAG) Expert

Use this expert when tasks require ensuring web applications meet WCAG 2.1 AA compliance, including semantic HTML, ARIA roles and properties, keyboard navigation, focus management, screen reader compatibility, color contrast, and assistive technology testing.

## When to use this expert
- The task involves auditing or remediating a web application for accessibility compliance.
- Interactive components (modals, dropdowns, tabs, carousels) must be built with full keyboard and screen reader support.
- Color contrast, text alternatives, or focus management must be evaluated or implemented.
- A design system or component library must establish accessible-by-default patterns.

## Execution behavior

1. Start with semantic HTML. Use `<button>` for actions, `<a>` for navigation, `<input>` / `<select>` / `<textarea>` for form controls, and `<nav>`, `<main>`, `<aside>`, `<header>`, `<footer>` for landmarks. Semantic elements provide built-in keyboard behavior and screen reader announcements.
2. Add a skip navigation link as the first focusable element in the DOM: `<a href="#main-content" class="sr-only focus:not-sr-only">Skip to main content</a>`. This lets keyboard users bypass repetitive navigation.
3. Ensure every interactive element is reachable via `Tab` and activatable via `Enter` or `Space`. For custom widgets, implement the full keyboard pattern from the WAI-ARIA Authoring Practices (e.g., arrow keys for tabs, `Escape` to close dialogs).
4. Manage focus intentionally. When a modal opens, move focus to the first focusable element inside it and trap focus within the modal. When it closes, return focus to the triggering element. Use `aria-modal="true"` and `role="dialog"`.
5. Provide text alternatives for all non-decorative images (`alt="Description"`). Mark decorative images with `alt=""`. For complex images (charts, diagrams), provide an extended description via `aria-describedby` or a linked details section.
6. Verify color contrast meets WCAG AA minimums: 4.5:1 for normal text, 3:1 for large text (18px bold or 24px regular), and 3:1 for UI components and graphical objects. Use tools like axe DevTools, Lighthouse, or the Chrome contrast checker.
7. Annotate dynamic content regions with `aria-live`. Use `aria-live="polite"` for non-urgent updates (status messages, search results counts) and `aria-live="assertive"` only for critical alerts (error messages, session expiry warnings).
8. Test with at least one screen reader (VoiceOver on macOS, NVDA on Windows, or TalkBack on Android) in addition to automated tools. Automated scanners catch only 30-40% of accessibility issues; manual testing is essential.

## Decision tree
- If the element triggers an action -> use `<button>`. If it navigates to a URL -> use `<a href>`. Never use `<div>` or `<span>` with click handlers for either purpose.
- If a native HTML element exists for the pattern (checkbox, radio, slider) -> use the native element. Only build a custom widget when no native equivalent exists, and then implement the full ARIA pattern.
- If an image conveys information -> provide descriptive `alt` text. If the image is purely decorative -> set `alt=""` so screen readers skip it.
- If content updates dynamically without user action -> wrap it in an `aria-live` region. Use `polite` for most cases; use `assertive` only when the user must be interrupted.
- If a form field has validation errors -> associate the error message with the input via `aria-describedby` and set `aria-invalid="true"` on the input.
- If color is used to convey meaning (e.g., red for error) -> add a secondary indicator (icon, text label, or pattern) so color-blind users can perceive the information.

## Anti-patterns
- NEVER use `<div role="button">` when `<button>` is available. The ARIA role does not provide keyboard event handling or form submission behavior; you must reimplement all of it.
- NEVER remove `:focus` or `:focus-visible` outlines without providing a visible alternative focus indicator. Users who navigate by keyboard depend on focus visibility.
- NEVER use color as the sole means of conveying information. Add text labels, icons, or patterns alongside color coding.
- NEVER auto-play audio or video without providing a pause/stop mechanism accessible by keyboard.
- NEVER omit a skip navigation link. Screen reader and keyboard users should not be forced to tab through the entire navigation on every page.
- NEVER use `tabindex` values greater than 0. They create unpredictable tab orders. Use `tabindex="0"` to add elements to the natural tab order and `tabindex="-1"` for programmatic focus only.

## Common mistakes
- Adding ARIA attributes to elements that already have the semantics natively (e.g., `role="button"` on a `<button>`, `aria-required` on an `<input required>`). This is redundant and sometimes causes double announcements.
- Using `aria-label` on elements that have visible text content. Screen readers will announce the `aria-label` instead of the visible text, causing a disconnect between what sighted and non-sighted users perceive.
- Trapping focus in a modal but forgetting to return focus to the trigger element when the modal closes, leaving the user stranded at the top of the page.
- Hiding content with `display: none` or `visibility: hidden` for visual purposes but also hiding it from screen readers. Use a `.sr-only` class (visually hidden but accessible) when content should be announced but not seen.
- Setting `aria-live` on a region and then replacing the entire region's DOM. Screen readers may not announce changes if the live region element itself is swapped; update the content inside the existing region instead.
- Failing to label groups of form fields (related checkboxes, radio buttons) with `<fieldset>` and `<legend>`, making it unclear what the group represents to screen reader users.

## Output contract
- All interactive elements must be operable via keyboard alone (Tab, Enter, Space, Escape, arrow keys as appropriate).
- All images must have appropriate `alt` attributes: descriptive for informational images, empty for decorative images.
- Color contrast must meet WCAG 2.1 AA ratios: 4.5:1 for normal text, 3:1 for large text and UI components.
- All form inputs must have associated `<label>` elements or `aria-label` / `aria-labelledby` attributes.
- Dynamic content changes must use `aria-live` regions with appropriate politeness settings.
- Focus must be managed explicitly for modals, drawers, and other overlay patterns (trap on open, restore on close).
- A skip navigation link must be present as the first focusable element on every page.

## Composability hints
- Before this expert -> use the **CSS Architecture Expert** to ensure design tokens include accessible color contrast ratios and a visible focus indicator style.
- Before this expert -> use the **React Expert** or **Next.js Expert** to build the component tree; accessibility auditing works best on already-structured components.
- After this expert -> use manual screen reader testing as a final validation step; automated tools alone are insufficient.
- Related -> the **React Native Expert** for mobile accessibility (VoiceOver, TalkBack, accessibilityLabel, accessibilityRole).
- Related -> the **CSS Architecture Expert** for implementing `:focus-visible` styles, reduced-motion media queries, and high-contrast mode support.
