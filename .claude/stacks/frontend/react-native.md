# Frontend stack guide: React Native (TypeScript)

Read by `fe-designer`, `fe-planner`, `fe-developer`, `fe-tester` and `fe-reviewer` when the
Project profile in `CLAUDE.md` names this guide. It maps the generic Atomic Design rules in the
skills to React Native. Works for bare React Native and Expo.

## Layout

Paths are relative to the mobile folder in the profile. Follow the repo's existing layout; if
none exists yet, use:

```
src/
  theme/            tokens: colors, typography, spacing, radii, shadows; ThemeProvider
  components/
    atoms/          <Name>/index.tsx, <Name>.test.tsx, (styles.ts)
    molecules/
    organisms/
    templates/
  screens/          <Name>Screen: template + data + navigation
  navigation/       navigators and typed route params (or app/ with Expo Router)
  services/api/     HTTP client and one module per backend context, typed with the contract
  hooks/            reusable hooks (data fetching, form logic)
  store/            client state, only when server state isn't enough
  types/            shared types (API DTO types mirror the backend contract)
  utils/
```

## Idioms

- TypeScript `strict`; no `any`; typed props, navigation params and API responses.
- Functional components and hooks.
- Styles from tokens only (`StyleSheet.create` or the repo's styling solution).
- Server state with the repo's data layer (default: TanStack Query) handling loading, error,
  retry, caching and invalidation; local UI state with `useState`/`useReducer`.
- Lists with `FlatList`/`FlashList`, stable `keyExtractor`, memoised rows when needed.
- `memo`, `useCallback`, `useMemo` where they help, not everywhere.
- Accessibility: `accessibilityRole`, `accessibilityLabel`, `hitSlop` or padding for 44 pt
  targets, respect font scaling.
- Safe areas with `react-native-safe-area-context`; `KeyboardAvoidingView` or the repo's
  keyboard solution.
- Tokens and secrets in Keychain/Keystore (`expo-secure-store`, `react-native-keychain`),
  never in AsyncStorage.
- API base URL from config (`app.config`/env), no `console.log` left behind.

## Testing

- Jest + React Native Testing Library for atoms, molecules, organisms and screens.
- API mocked with MSW or the repo's mocking approach, built from the contract.
- E2E with Maestro or Detox if the repo has it.
- Screenshots: simulator/emulator captures, Maestro `takeScreenshot`, or Expo web with
  Playwright at the profile's phone widths.

## Default commands

```
npx jest <paths>    # tests for one slice
npm test            # full suite
npm run lint
npx tsc --noEmit
npx expo start      # or npx react-native run-ios / run-android
```

## Review checklist additions

- Hooks rules respected; effects with correct dependencies and cleanup; no stale closures.
- Lists virtualised; images sized and cached (`expo-image` or equivalent).
- Platform-specific code (`Platform.select`, `.ios.tsx`/`.android.tsx`) only where needed.
- No AsyncStorage for anything sensitive.
