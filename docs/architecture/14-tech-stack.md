# 14. Tech Stack

This document outlines the technology stack for the Huge IFX Soccer project, as derived from project standards and the Product Requirements Document (PRD).

## Backend

- **Language:** Python 3.13
- **Framework:** FastAPI
- **Package Manager:** Poetry
- **Containerization:** Docker
- **Vector Store:** In-memory, using LangChain with FAISS.
- **LLM:** A high-performance model from a major provider (e.g., Google, OpenAI, Anthropic).

## Frontend

- **Language:** JavaScript/TypeScript
- **Framework:** React
- **Build Tool:** Vite
- **UI Library:** shadcn/ui

## Development & Infrastructure

- **Repository:** GitHub
- **Development Environment:** GeminiCLI
- **Hosting:** Vercel (for both frontend and backend services).
- **Communication:** WebSockets for real-time, bidirectional communication between frontend and backend.
