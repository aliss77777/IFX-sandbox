# Code Style

## Python

- **Formatting:** We use single quotes (`'`) for strings unless a double quote (`"`) is required within the string. We use `ruff` to format and lint our code.
- **Typing:** All function signatures must have type hints. No exceptions.
- **Paths:** Use the `pathlib` library for all filesystem path manipulations. It's cleaner and more expressive.

### Unit tests

- All unit and integration tests must use the `pytest` framework.
- Prefer using `pytest` markers (e.g., `@pytest.mark.integration`) to distinguish test types.
- Each test function should include a docstring describing its intent.
- Assertions should include helpful error messages for easier debugging.
- Tests should be simple, readable, and leverage pytest features (fixtures, parametrization, etc.) where beneficial.
