# R2 GitHub Actions Unzipper - Coding Guidelines

## Build & Test Commands
- Build: `npm run build` 
- Lint: `npm run lint`
- Test (all): `npm run test`
- Test (single file): `npm test -- -t "test name"` or `jest path/to/test.js`
- Dev mode: `npm run dev`

## Code Style Guidelines
- **Formatting**: Use Prettier with default config
- **Linting**: ESLint with Airbnb preset
- **Types**: TypeScript with strict mode enabled
- **Imports**: Group by external/internal, alphabetize
- **Naming**: camelCase for variables/functions, PascalCase for classes/interfaces
- **Error Handling**: Use try/catch for async operations, avoid silent failures
- **Comments**: JSDoc for public APIs, inline for complex logic
- **Max Line Length**: 100 characters

## Notes
- Commit often with descriptive messages
- Update this file as the codebase evolves