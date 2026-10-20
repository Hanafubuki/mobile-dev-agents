# Stack guides

The role skills in `.claude/skills/` hold the rules that apply to every stack: DDD layering,
DTOs and TDD on the backend, Atomic Design and every-state screens on the frontend. A stack
guide maps those rules to one framework. The Project profile in `CLAUDE.md` names the backend
guide and the frontend guide the project uses.

Included:

- `backend/laravel.md`: Laravel (PHP)
- `frontend/react-native.md`: React Native / Expo (TypeScript)

## Adding a stack

Copy the closest guide, name it after the stack (`backend/nestjs.md`, `backend/django.md`,
`frontend/flutter.md`, `frontend/swiftui.md`…), point the profile at it, and keep the same
five sections so every skill finds what it looks for:

1. **Layout**: the folder structure for each layer (backend: Domain, Application,
   Infrastructure, HTTP and tests; frontend: theme, atoms → templates, screens, navigation,
   API client, state, tests).
2. **Idioms**: how the generic rules are written in this stack (DTO type, thin controller
   pipeline, dependency injection, styling, data layer, secure storage…).
3. **Testing**: test framework, how the database or API is set up in tests, E2E tool, how
   screenshots are taken.
4. **Default commands**: scoped tests, full suite, lint/format, type check, run locally. The
   profile overrides them.
5. **Review checklist additions**: stack-specific checks the reviewer adds to the generic list.
