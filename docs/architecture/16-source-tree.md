# 16. Source Tree

This document describes the source tree structure for the Huge IFX Soccer monorepo.

## Monorepo Structure

The project is organized as a monorepo to simplify development and dependency management. The primary directories are:

- **`/app`**: Contains the backend Python application, built with FastAPI.
- **`/ifx-app`**: Contains the frontend React application, built with Vite.
- **`/docs`**: Contains all project documentation, including the PRD and architecture documents.
- **`/data`**: Contains data for the fictional Huge League, including teams, players, and logos.
- **`/tests`**: Contains tests for the application.
- **`/.bmad-core`**: Contains the configuration and tasks for the BMad development methodology.
- **`/.gemini`**: Contains configuration and context for the Gemini CLI.
