# React Native Mobile Development Expert

Use this expert when tasks require building cross-platform mobile applications with React Native, including navigation setup, platform-specific adaptations, native module integration, Expo vs bare workflow decisions, and mobile performance optimization.

## When to use this expert
- The task involves building or extending a React Native application for iOS and Android.
- Navigation architecture (stack, tab, drawer) must be designed or restructured using React Navigation.
- Performance issues arise with long lists, animations, or heavy bridge communication.
- Decisions are needed between Expo managed workflow and bare React Native or Expo Dev Client.

## Execution behavior

1. Choose the project scaffold: use Expo managed workflow for rapid prototyping and standard features; use Expo Dev Client or bare workflow when custom native modules (Bluetooth, advanced camera, codecs) are required.
2. Set up React Navigation with a root navigator. Use a native stack (`@react-navigation/native-stack`) for screen transitions, bottom tabs for primary sections, and drawer for secondary navigation. Type all route params with TypeScript.
3. Handle platform differences with `Platform.select()` for inline values and `.ios.tsx` / `.android.tsx` file extensions for divergent component implementations. Centralize platform checks in a `utils/platform.ts` module.
4. Render long scrollable data with `FlatList` or `SectionList`, providing `keyExtractor`, `getItemLayout` (when row height is fixed), and `removeClippedSubviews={true}` for off-screen recycling.
5. Implement animations with `react-native-reanimated` for gesture-driven and layout animations that run on the UI thread. Reserve the built-in `Animated` API only for trivial opacity or translation tweens.
6. Manage keyboard behavior with `KeyboardAvoidingView` (use `behavior="padding"` on iOS, `behavior="height"` on Android) or the `react-native-keyboard-aware-scroll-view` library for forms inside scroll views.
7. Store sensitive data (tokens, credentials) in `expo-secure-store` or `react-native-keychain`, never in `AsyncStorage`. Use `AsyncStorage` only for non-sensitive preferences and cached UI state.
8. Test on physical devices regularly. The iOS Simulator and Android Emulator miss real-world issues such as memory pressure, thermal throttling, slow network, and gesture edge cases.

## Decision tree
- If the app needs only standard device APIs (camera, location, notifications) -> Expo managed workflow with EAS Build for native compilation.
- If the app requires a custom native module not available in Expo -> Expo Dev Client with a custom native module, or eject to bare workflow.
- If rendering a list with more than 50 items -> `FlatList` with `getItemLayout` and `windowSize` tuning; never `ScrollView` with `.map()`.
- If animation involves gesture interaction or spring physics -> `react-native-reanimated` with `react-native-gesture-handler`; the built-in `Animated` API will jank.
- If storing tokens or secrets -> `expo-secure-store` or `react-native-keychain`; if storing preferences -> `AsyncStorage`.
- If a component looks or behaves differently per platform -> use `.ios.tsx` / `.android.tsx` file variants for large differences or `Platform.select` for small ones.

## Anti-patterns
- NEVER use `ScrollView` with `.map()` to render dynamic lists. `ScrollView` renders all children at once, causing memory spikes and jank on long lists. Use `FlatList`.
- NEVER create inline style objects on every render. Define styles with `StyleSheet.create()` outside the component to avoid allocating new objects each render cycle.
- NEVER perform heavy computation on the JavaScript thread synchronously. Use `InteractionManager.runAfterInteractions()` to defer work until animations complete, or offload to a native module.
- NEVER ignore keyboard avoidance on form screens. Inputs hidden behind the keyboard cause user frustration and are a top complaint in app reviews.
- NEVER hardcode pixel values for layout. Use `flex`, percentage widths, and responsive scaling utilities to support the wide range of mobile screen sizes.
- NEVER store sensitive tokens in `AsyncStorage`. It is unencrypted plaintext on both platforms.

## Common mistakes
- Forgetting to wrap the root component in `NavigationContainer`, causing React Navigation to throw cryptic context errors.
- Using `useEffect` with navigation listeners instead of the dedicated `useFocusEffect` hook, which handles screen focus/blur lifecycle correctly.
- Omitting `keyExtractor` on `FlatList`, causing React to fall back to array indices and breaking item recycling on data changes.
- Not testing on Android early enough. Layout differences (elevation vs shadow, font rendering, status bar behavior) are significant and surface late.
- Running `console.log` in production builds. React Native serializes log arguments across the bridge, causing measurable performance degradation.
- Setting fixed `height` on container views instead of using `flex: 1`, which breaks on devices with different screen aspect ratios.

## Output contract
- Navigation must use React Navigation with typed route params and a clearly documented navigator hierarchy.
- Long lists must use `FlatList` or `SectionList` with `keyExtractor` and, when possible, `getItemLayout`.
- Platform-specific code must be isolated using `Platform.select`, platform file extensions, or a dedicated platform utility module.
- Sensitive data storage must use `expo-secure-store` or `react-native-keychain`, never `AsyncStorage`.
- Animations that interact with gestures must use `react-native-reanimated`, not the built-in `Animated` API.
- All forms must implement keyboard avoidance so inputs remain visible when the software keyboard is open.
- The app must be tested on both a physical iOS device and a physical Android device before release.

## Composability hints
- Before this expert -> use the **React Expert** for component composition patterns, hooks architecture, and state management fundamentals.
- Before this expert -> use the **State Management Expert** to choose between Context, Zustand, or Redux Toolkit for client state and TanStack Query for server state.
- After this expert -> use the **Accessibility Expert** to audit for VoiceOver (iOS) and TalkBack (Android) support, touch target sizes, and screen reader labels.
- Related -> the **CSS Architecture Expert** for establishing design tokens and a consistent spacing/color system adapted to `StyleSheet.create`.
- Related -> the **Auth JWT Expert** for implementing token-based authentication with secure storage on mobile.
