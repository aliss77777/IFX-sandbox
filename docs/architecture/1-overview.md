# 1. Overview

This document outlines the full-stack architecture for the Huge IFX Soccer AI Demo. The system is designed as a real-time, conversational AI application that allows users to interact with a fictional soccer league through a chat-based interface. The architecture prioritizes a decoupled, modular design to facilitate rapid development, testing, and future scalability.

The core of the application is a real-time streaming architecture using WebSockets to provide a responsive and engaging user experience. The system is composed of a Next.js frontend and a Python/FastAPI backend, deployed in a monorepo structure.
