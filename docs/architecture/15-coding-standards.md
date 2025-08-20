# 15. Coding Standards

This document outlines the coding standards and conventions to be followed for the Huge IFX Soccer project. These are based on the global standards defined for the project.

## Python (Backend)

- **Formatting:** We use single quotes (`'`) for strings unless a double quote (`"`) is required within the string. We use `ruff` to format and lint our code.
- **Typing:** All function signatures must have type hints. No exceptions.
- **Paths:** Use the `pathlib` library for all filesystem path manipulations. It's cleaner and more expressive.

### Unit tests

- All unit and integration tests must use the `pytest` framework.
- Prefer using `pytest` markers (e.g., `@pytest.mark.integration`) to distinguish test types.
- Each test function should include a docstring describing its intent.
- Assertions should include helpful error messages for easier debugging.
- Tests should be simple, readable, and leverage pytest features (fixtures, parametrization, etc.) where beneficial.

## Frontend

### Unit and Component Tests

-   **Framework:** We use [Jest](https://jestjs.io/) for running tests and [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) for rendering and interacting with components.
-   **Configuration:** Jest is configured for Next.js using the `next/jest` preset in `ifx-app/jest.config.js`.
-   **Test Files:** Test files should be located alongside the component they are testing, with the `.test.tsx` extension (e.g., `chat-input.test.tsx`).
-   **Running Tests:** Tests can be run from the `ifx-app` directory using the `npm test` command.
