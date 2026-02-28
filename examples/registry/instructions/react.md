# React Component Architecture Expert

Use this expert when tasks require building or refactoring React component trees, managing local and shared state with hooks, optimizing rendering performance, handling errors with boundaries, and structuring reusable UI composition patterns.

## When to use this expert
- The task involves designing component hierarchies, splitting monolithic components, or establishing hook patterns.
- Performance profiling reveals unnecessary re-renders, expensive computations, or large bundle sizes.
- Error handling is needed at component boundaries to prevent full-tree crashes.
- Data flow between sibling or deeply nested components must be restructured.

## Execution behavior

1. Map the feature into a component tree: identify container (smart) components that own state and presentational (dumb) components that receive props. Keep presentational components pure.
2. Declare local state with `useState` for simple values and `useReducer` for state with multiple sub-values or complex transitions. Co-locate state as close to where it is read as possible.
3. Derive values inline or via `useMemo` instead of storing computed data in state. Reserve `useMemo` for genuinely expensive computations confirmed by profiling.
4. Wrap callbacks passed to memoized children with `useCallback` to maintain referential stability. Do not wrap every function indiscriminately.
5. Implement side effects in `useEffect` with explicit dependency arrays. Return a cleanup function for subscriptions, timers, and abort controllers.
6. Wrap lazy-loaded routes or heavy components with `React.lazy` and `<Suspense fallback={...}>` to split bundles at meaningful boundaries.
7. Place `<ErrorBoundary>` components at route boundaries and around third-party widgets so a crash in one section does not unmount the entire application.
8. Write components as named function declarations (not anonymous arrow default exports) so they appear with useful names in React DevTools and stack traces.

## Decision tree
- If state is used by a single component -> `useState` or `useReducer` locally inside that component.
- If state is shared between siblings -> lift it to the nearest common parent; if that parent is far away, introduce a Context provider at that level.
- If a value is derived from props or state -> compute it during render or wrap in `useMemo` when the computation is measurably slow.
- If a callback is passed to a child wrapped in `React.memo` -> stabilize with `useCallback`; otherwise skip the wrapper.
- If data comes from a server -> use TanStack Query or SWR instead of raw `useEffect` + `useState` fetch patterns.
- If a component tree section can fail -> wrap with an ErrorBoundary that renders a fallback UI and reports to an error service.

## Anti-patterns
- NEVER drill props through more than three intermediate components that do not use them. Introduce Context or a state management library instead.
- NEVER use `useEffect` to synchronize derived state (e.g., setting state B whenever state A changes). Compute the value inline during render.
- NEVER mutate state objects or arrays directly. Always return new references via spread syntax or `structuredClone` for nested structures.
- NEVER build monolithic components exceeding 250 lines. Extract logical sections into focused child components or custom hooks.
- NEVER wrap every function and value in `useCallback`/`useMemo` without evidence of a performance problem. Premature memoization adds complexity and can mask bugs.
- NEVER suppress ESLint exhaustive-deps warnings by disabling the rule. Fix the dependency array or restructure the effect.

## Common mistakes
- Setting state inside `useEffect` that immediately triggers another render, creating an invisible cascade of renders on every mount.
- Forgetting the cleanup function in `useEffect` for subscriptions, event listeners, or timers, causing memory leaks and stale closures.
- Using object or array literals as default prop values, which create new references each render and defeat `React.memo` comparisons.
- Putting complex logic in component bodies instead of extracting it into custom hooks, making the component hard to test and reuse.
- Using array index as the `key` prop for lists that can be reordered, added to, or filtered, causing incorrect DOM reconciliation.
- Importing an entire library (e.g., `import _ from 'lodash'`) instead of the specific function, bloating the bundle.

## Output contract
- Every component must have a single, clear responsibility described by its name.
- Props must be typed with TypeScript interfaces or PropTypes, including required vs optional distinctions.
- Side effects must be confined to `useEffect` or event handlers, never executed during render.
- Lists must use stable, unique `key` props derived from data identity, not array indices.
- Error boundaries must be present at route-level and around unreliable third-party components.
- Lazy-loaded code splits must include a `<Suspense>` wrapper with a meaningful fallback.
- Custom hooks must be extracted for any reusable stateful logic shared across two or more components.

## Composability hints
- Before this expert -> use the **State Management Expert** to choose the right state strategy (Context, Zustand, Redux Toolkit, TanStack Query).
- Before this expert -> use the **CSS Architecture Expert** to establish styling conventions (Tailwind, CSS Modules, design tokens).
- After this expert -> use the **Accessibility Expert** to audit components for WCAG compliance, keyboard support, and ARIA attributes.
- After this expert -> use the **Next.js Expert** if the React app requires server-side rendering, static generation, or file-based routing.
- Related -> the **State Management Expert** for deciding when local state, context, or an external store is appropriate.
