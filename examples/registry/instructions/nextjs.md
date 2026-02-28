# Next.js Application Framework Expert

Use this expert when tasks require building full-stack web applications with Next.js App Router, including server and client component architecture, data fetching strategies, middleware, rendering modes (SSG/SSR/ISR), metadata for SEO, and loading/error state management.

## When to use this expert
- The task involves creating or restructuring a Next.js application using the App Router (app directory).
- Decisions are needed about server components vs client components and where the "use client" boundary should be placed.
- Data fetching must be designed across server components, route handlers, or server actions.
- SEO, performance, or rendering strategy (static vs dynamic vs incremental) must be chosen for specific routes.

## Execution behavior

1. Structure the `app/` directory with route segments as folders. Each route folder contains `page.tsx` (UI), `layout.tsx` (shared shell), `loading.tsx` (streaming fallback), and `error.tsx` (error boundary).
2. Default every component to a server component. Only add `"use client"` when the component requires browser APIs, event handlers, `useState`, or `useEffect`. Push the client boundary as far down the tree as possible.
3. Fetch data directly in server components using `async/await` with the extended `fetch` API. Configure caching via `{ next: { revalidate: N } }` for ISR or `{ cache: "no-store" }` for fully dynamic pages.
4. Use route handlers (`app/api/.../route.ts`) for webhook endpoints, third-party callbacks, or any logic that must respond to non-GET HTTP methods from external services. For form submissions from your own UI, prefer server actions.
5. Implement `generateMetadata` or export a static `metadata` object in each `page.tsx` and `layout.tsx` to provide title, description, Open Graph, and Twitter card data for SEO.
6. Use `generateStaticParams` in dynamic route segments to pre-render known paths at build time (SSG). Combine with `dynamicParams = true` to allow on-demand ISR for new paths.
7. Add middleware in `middleware.ts` at the project root for cross-cutting concerns: authentication redirects, geo-based routing, A/B testing headers, and request logging. Keep middleware lightweight since it runs on every matching request.
8. Use `loading.tsx` files to provide instant streaming fallbacks while server components resolve. Pair with `<Suspense>` inside layouts for more granular streaming boundaries.

## Decision tree
- If content is the same for all users and changes infrequently -> SSG with `generateStaticParams`; use ISR (`revalidate`) if it updates periodically.
- If content depends on the request (cookies, headers, search params) -> server component reading `cookies()` or `headers()` with `dynamic = "force-dynamic"`.
- If content must update in real time in the browser -> client component with SWR, TanStack Query, or WebSocket subscription.
- If a page needs authentication gating -> use `middleware.ts` to redirect unauthenticated requests before the page even renders.
- If a page needs SEO metadata -> export `generateMetadata` to dynamically produce title, description, and OG tags from fetched data.
- If a form submits data -> use a server action (`"use server"` function) with `useFormStatus` for pending UI, rather than a client-side fetch to an API route.

## Anti-patterns
- NEVER add `"use client"` to layout or page files that do not require interactivity. This opts the entire subtree out of server rendering and data fetching benefits.
- NEVER fetch data in `useEffect` inside client components when the same data could be fetched in a parent server component and passed as props.
- NEVER omit `loading.tsx` or `<Suspense>` boundaries for routes with async data. Users will see a blank screen during server-side data fetching.
- NEVER import server-only modules (`fs`, `database clients`, secrets) in client components. Use the `server-only` package to create a build-time error if this happens.
- NEVER use the Pages Router (`pages/` directory) conventions in an App Router project. The two routers have incompatible data fetching and layout models.
- NEVER put heavy computation or slow database queries in middleware. Middleware runs on the Edge Runtime and should only inspect/modify the request or redirect.

## Common mistakes
- Marking a top-level layout as `"use client"` to add a single click handler, which forces every nested page into client rendering. Extract only the interactive piece into a small client component.
- Forgetting that `fetch` in server components is deduplicated and cached by default. Adding manual caching layers on top creates stale data bugs.
- Using `redirect()` inside a try/catch block, which catches the redirect throw and prevents navigation. Call `redirect()` outside of try/catch.
- Not setting `revalidate` on `fetch` calls in ISR pages, defaulting to permanent caching and serving stale content indefinitely.
- Passing non-serializable values (functions, class instances) from server components to client components as props, causing runtime hydration errors.
- Creating API route handlers for data that is only consumed by your own pages, when a server component fetch or server action would be simpler and faster.

## Output contract
- Every route segment must include `page.tsx` and should include `loading.tsx` and `error.tsx` for complete UX coverage.
- Server components must be the default; `"use client"` must only appear on leaf components that need interactivity.
- All pages with public URLs must export `metadata` or `generateMetadata` with at minimum a title and description.
- Dynamic routes that have a known set of params must implement `generateStaticParams` for build-time pre-rendering.
- Authentication and authorization redirects must be handled in `middleware.ts`, not in individual page components.
- Data mutations must use server actions or route handlers, never direct database calls from client components.
- Environment variables containing secrets must only be accessed in server components, route handlers, or server actions (no `NEXT_PUBLIC_` prefix).

## Composability hints
- Before this expert -> use the **React Expert** to design component composition, hooks patterns, and error boundary strategy.
- Before this expert -> use the **CSS Architecture Expert** to set up Tailwind, CSS Modules, or design tokens within the Next.js project.
- After this expert -> use the **Accessibility Expert** to audit pages for semantic HTML, keyboard navigation, and ARIA attributes.
- After this expert -> use the **Auth JWT Expert** for implementing authentication flows in middleware and server actions.
- Related -> the **State Management Expert** for client-side state in interactive sections of an otherwise server-rendered app.
