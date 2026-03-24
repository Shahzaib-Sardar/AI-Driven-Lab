# expense-tracking-app Copilot Instructions

## Setup Checklist Status
- [x] Verify that the copilot-instructions.md file in the .github directory is created.
- [x] Clarify Project Requirements
- [x] Scaffold the Project
- [x] Customize the Project
- [x] Install Required Extensions
- [x] Compile the Project
- [x] Create and Run Task
- [ ] Launch the Project
- [x] Ensure Documentation is Complete

## Coding Standards
- Backend: Use Flask blueprints, keep endpoint handlers thin, move business logic into services as complexity grows.
- Frontend: Use functional React components with hooks and keep network calls in dedicated API modules.
- Validation: Validate and sanitize user input on both client and server.
- Security: Never store plain passwords; use secure hashing and token/session handling before production.
- Naming: Use `snake_case` in Python and `camelCase`/`PascalCase` conventions in React.
- Testing: Add unit tests for budget calculations and transaction totals before release.

## Domain Guidance
- Preserve transaction integrity (positive amounts, valid type/date, user ownership checks).
- Keep category deletion safe by blocking or reassigning categories in active use.
- Budget features should support overall and per-category monthly limits.
- Exports must support CSV for MVP.
