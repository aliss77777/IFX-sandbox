# Development Best Practices

## Preface 

Perfer someone build the api in a container. This will come up with
all the dependencies to run the api as well as a debugger, gemini-cli and any other development tools needed.

### Makefile

The Makefile contains a number of useful commands for development, deployment, and can be viewed for examples.

### Editor

- Editor: VSCode
- Container: Docker
- Container Editor: VSCode Remote - Containers

## Core Principles

### Keep It Simple
- Implement code in the fewest lines possible
- Avoid over-engineering solutions
- Choose straightforward approaches over clever ones

### Optimize for Readability
- Prioritize code clarity over micro-optimizations
- Write self-documenting code with clear variable names
- Add comments for "why" not "what"

### DRY (Don't Repeat Yourself)
- Extract repeated business logic to private methods
- Extract repeated UI markup to reusable components
- Create utility functions for common operations

### File Structure
- Keep files focused on a single responsibility
- Group related functionality together
- Use consistent naming conventions

## Dependencies

### Choose Libraries Wisely
When adding third-party dependencies:
- Select the most popular and actively maintained option
- Check the library's GitHub repository for:
  - Recent commits (within last 6 months)
  - Active issue resolution
  - Number of stars/downloads
  - Clear documentation

### Inspect Libraries
When encountering errors or writing code with unfamiliar
libraries consider the following:
- Using context7 MCP
- inspect the code in the container
- find the code on github
- following links in the tech-stack.md