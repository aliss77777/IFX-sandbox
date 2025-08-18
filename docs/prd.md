# Huge IFX Soccer Product Requirements Document (PRD)

### 1. Goals and Background Context

#### 1.1. Goals

*   Create a "Wow" Factor Demo to serve as the centerpiece of the IX sales pitch.
*   Empower the Sales Team with an interactive tool to demonstrate Huge's value in the AI space.
*   Accelerate Internal Expertise by testing new AI tools and documenting reusable IX patterns.
*   Provide a convincing experience for a Casual Fan, making them feel informed and engaged.
*   Achieve on-time delivery of the MVP demo.

#### 1.2. Background Context

The sports industry is struggling to engage younger, digitally-native fans and effectively leverage data. At the same time, Huge's most impressive AI work is protected by NDAs, hindering our ability to showcase our capabilities to potential clients in the sports, media, and entertainment sectors.

This project solves both problems by creating a publicly-accessible AI demo built around a fictional soccer league. It will serve as a tangible example of our Intelligent Fan Experiences (IX) offering, proving our ability to build the personalized, AI-native experiences that modern fans expect and demonstrating our value as a strategic innovation partner.

#### 1.3. Change Log

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-08-18 | 1.0 | Initial draft based on Project Brief | John (PM) |

### 2. Requirements

#### 2.1. Functional

*   **FR1:** The system must provide a chat-based interface for users to submit natural language queries.
*   **FR2:** The system must use vector search to find the most relevant asset (e.g., player image, team logo) from a content library based on the user's query.
*   **FR3:** The system must display the retrieved asset prominently in the user interface.
*   **FR4:** The system must generate conversational text that answers the user's question and provides context about the displayed asset.
*   **FR5:** The system must support multi-turn conversations, remembering the context of the current session to handle follow-up questions.
*   **FR6:** The system must provide session-based personalization, such as remembering a user's favorite team within a single session.
*   **FR7:** The system must include a pre-defined "canned" demo flow of questions and interactions.
*   **FR8:** The content library must contain 4 fictional teams with logos and descriptions.
*   **FR9:** The content library must contain 23 fictional players per team with profile pictures and basic attributes.

#### 2.2. Non-Functional

*   **NFR1:** The application must be deployed to a stable, public URL for demo purposes.
*   **NFR2:** The user interface must be polished and align with Huge's brand standards.
*   **NFR3:** The backend application must be containerized using Docker.
*   **NFR4:** The system architecture must be modular to allow for easy swapping of components (e.g., LLM, vector store).
*   **NFR5:** The system must be performant enough for a real-time demo, with responses generated in a timely manner.
*   **NFR6:** The application must use a real-time communication protocol (WebSockets) to stream responses from the backend to the frontend. This is to ensure a responsive user experience where text can appear token-by-token and assets can be displayed as soon as they are identified.

### 3. User Interface Design Goals

#### 3.1. Overall UX Vision

The user experience will be clean, modern, and "asset-first." The primary focus will be on the visual content (player images, team logos), with the conversational text acting as a supportive layer. The interface should feel premium, responsive, and immediately engaging, aligning with Huge's reputation for high-quality design.

#### 3.2. Key Interaction Paradigms

*   **Conversational Search:** The core interaction is a simple, chat-like input where the user asks questions naturally.
*   **Visual Discovery:** The output is primarily visual. Instead of just text answers, the system presents rich media assets that the user can explore.
*   **Progressive Disclosure:** Information is revealed contextually. The user gets a primary asset first, with more details and related chatter available upon request or through follow-up questions.

#### 3.3. Core Screens and Views

*   **Main Chat/Search View:** The primary interface where the user interacts with the AI, sees the conversation history, and views the returned assets. This view must include an optional developer/debug panel to display underlying I/O (e.g., LLM prompts, vector search results) for demonstration purposes.
*   **Asset Detail View (Modal):** A larger, more detailed view that appears when a user clicks on a returned asset, showing key attributes or stats.

#### 3.4. Accessibility

*   **Best Effort / shadcn/ui:** The project will make a best effort to be accessible, leveraging the built-in accessibility features provided by the `shadcn/ui` component library.

#### 3.5. Branding

*   The UI will align with Huge's brand standards, using a clean, sophisticated aesthetic. Specific brand guidelines will be incorporated once provided.

#### 3.6. Target Device and Platforms

*   **Web Responsive:** The application will be designed to work flawlessly on modern web browsers across desktop, tablet, and mobile devices.

### 4. Technical Assumptions

#### 4.1. Repository Structure

*   **Monorepo:** The project will use a monorepo to simplify development, dependency management, and deployment, especially with a small team. The frontend and backend code will live in separate, modular directories within this single repository to allow for a potential split in the future.

#### 4.2. Service Architecture

*   **Decoupled Services:** The architecture will feature a decoupled frontend application and a backend API service, developed as modular components within the monorepo. This enforces a clean separation of concerns and allows for independent development and scaling of the services, even within a single repository.

#### 4.3. Testing Requirements

*   **Unit + Integration:** The testing strategy will include both unit tests for individual components and integration tests to ensure the frontend and backend services communicate correctly.

#### 4.4. Additional Technical Assumptions and Requests

*   **Language (Backend):** The backend will be built using Python and the FastAPI framework.
*   **Language (Frontend):** The frontend will be built using JavaScript/TypeScript with the React framework and Vite build tool.
*   **UI Components:** The `shadcn/ui` component library will be used for the frontend.
*   **Vector Store:** The MVP will use a simple, in-memory vector store (e.g., from LangChain or a similar library).
*   **Containerization:** The backend application must be containerized using Docker.
*   **Hosting (Frontend):** The frontend will be hosted on Vercel.
*   **Hosting (Backend):** The backend will be hosted on Vercel if feasible, otherwise on a suitable container-hosting platform.
*   **LLM:** A high-performance LLM from a major provider (e.g., Google, OpenAI, Anthropic) will be used. The specific model will be chosen based on performance and cost analysis.

### 5. Epic List

*   **Epic 1: Foundation & Streaming Architecture:**
    *   **Goal:** Establish the foundational monorepo structure, a working UI, and a **proven, end-to-end real-time streaming architecture**. This epic will deliver a functional, deployable application that demonstrates the core WebSocket communication pattern with dummy/hardcoded data, ensuring the riskiest technical component works before adding the AI logic.
*   **Epic 2: AI Integration:**
    *   **Goal:** Layer the AI-powered features onto the proven streaming architecture. This epic will replace the hardcoded responses from Epic 1 with live vector search results and real, generative LLM responses.

### 6. Epic 1: Foundation & Streaming Architecture

**Goal:** Establish the foundational monorepo structure, a working UI, and a **proven, end-to-end real-time streaming architecture**. This epic will deliver a functional, deployable application that demonstrates the core WebSocket communication pattern with dummy/hardcoded data, ensuring the riskiest technical component works before adding the AI logic.

#### Story 1.1: Monorepo Structure & `ifx-app` Scaffolding
*As a developer, I want to formalize the monorepo structure and scaffold the new `ifx-app` frontend application, so that all project components are logically organized and ready for development.*
*   **Acceptance Criteria:**
    1.  The existing `app` directory is confirmed as the location for the Python/FastAPI backend.
    2.  A new `ifx-app` directory is created at the project root (`/workspace/ifx-app`).
    3.  A new Vite + React (TypeScript) application is scaffolded inside the `ifx-app` directory.
    4.  The root `README.md` is updated with a clear explanation of the monorepo structure (`app` for backend, `ifx-app` for frontend) and instructions on how to run each service.
    5.  The existing Docker setup is reviewed and confirmed to be sufficient for running the backend service.

#### Story 1.2: Basic Frontend UI
*As a user, I want to see a basic chat interface with an input box and a message display area, so that I can begin to interact with the application.*
*   **Acceptance Criteria:**
    1.  The main application view renders a chat-style interface.
    2.  A text input field is present at the bottom of the screen.
    3.  A "Send" button is present next to the input field.
    4.  A display area for conversation history is present.
    5.  The UI uses basic `shadcn/ui` components for the inputs and buttons.
    6.  The UI is responsive and usable on both mobile and desktop screens.

#### Story 1.3: Backend Health Check & WebSocket Endpoint
*As a developer, I want to add a health check and an initial WebSocket endpoint to the backend service, so that I can confirm the service is running and ready for real-time communication.*
*   **Acceptance Criteria:**
    1.  A `/health` endpoint is implemented and working.
    2.  A `/ws` endpoint is created in the FastAPI application that can accept WebSocket connections.

#### Story 1.4: Streaming "Hello World"
*As a developer, I want to implement a "hello world" that streams a sample image and text over a WebSocket, so that I can prove the core real-time architecture is working end-to-end.*
*   **Acceptance Criteria:**
    1.  The `ifx-app` establishes a persistent WebSocket connection to the `/ws` endpoint.
    2.  When the user sends a message, the backend immediately sends a WebSocket message containing a hardcoded image URL (e.g., `{"type": "asset", ...}`).
    3.  The `ifx-app` displays the image.
    4.  The backend then sends a stream of hardcoded `text_chunk` messages.
    5.  The `ifx-app` renders these chunks as a "typing" text effect.
    6.  The backend sends a final `stream_end` message.

#### Story 1.5: Continuous Deployment Setup
*As a developer, I want to set up continuous deployment for the application on Vercel, so that any changes pushed to the main branch are automatically deployed.*
*   **Acceptance Criteria:**
    1.  The monorepo is connected to a Vercel project.
    2.  Vercel is configured to correctly build and deploy the frontend application from the `ifx-app` directory.
    3.  Vercel is configured to correctly build and deploy the backend Docker container from the `app` directory.
    4.  A successful push to the `main` branch triggers a new deployment on Vercel.
    5.  The deployed application is accessible via a public Vercel URL.

### 7. Epic 2: AI Integration

**Goal:** Layer the AI-powered features onto the proven streaming architecture. This epic will replace the hardcoded responses from Epic 1 with live vector search results and real, generative LLM responses.

#### Story 2.1: Content Loading & In-Memory Vector Store
*As a developer, I want to load the fictional team and player data into an in-memory vector store at application startup, so that the content is ready for searching.*
*   **Acceptance Criteria:**
    1.  A service is created in the backend to read the team and player JSON files from the `/data/huge-league/players` directory.
    2.  An in-memory vector store (e.g., using LangChain/FAISS) is initialized when the backend application starts.
    3.  The player and team data is processed and loaded into the vector store.
    4.  The vector store creation does not significantly increase the application's startup time.

#### Story 2.2: Vector Search Integration
*As a developer, I want to replace the hardcoded image response with a real vector search result, so that the application can find assets relevant to the user's query.*
*   **Acceptance Criteria:**
    1.  The backend's WebSocket handler is modified to perform a similarity search on the vector store.
    2.  The handler sends an `asset` message over the WebSocket containing the *actual* matched item's data, replacing the hardcoded image URL.

#### Story 2.3: LLM Integration for Streaming Text
*As a user, I want to receive a natural language response generated by an LLM that is relevant to my query, so that the conversation is intelligent and contextual.*
*   **Acceptance Criteria:**
    1.  The backend's WebSocket handler is modified to call a real LLM in streaming mode, replacing the hardcoded text stream.
    2.  The prompt to the LLM includes the user's query and the data from the vector search result.
    3.  The LLM's streaming response is relayed chunk-by-chunk over the WebSocket.

#### Story 2.4: Multi-Turn Conversation & Session Personalization
*As a user, I want the application to remember what we just talked about and my favorite team, so that I can ask follow-up questions and have a more personalized experience.*
*   **Acceptance Criteria:**
    1.  The backend maintains a short-term conversation history for each WebSocket session.
    2.  When the user asks a follow-up question, the conversation history is passed to the LLM to provide context.
    3.  The system can correctly answer questions that rely on the previous turn's context.
    4.  A mechanism is implemented to identify and store a user's favorite team for the duration of the session.
    5.  Subsequent LLM prompts include the user's favorite team to allow for more personalized responses.

### 8. Checklist Results Report

_(This section will be populated by the Product Owner (PO) after they execute the `pm-checklist` against this document to ensure its quality and completeness.)_

### 9. Next Steps

#### 9.1. UX Expert Prompt

`*ux-expert` Here is the approved Product Requirements Document (PRD). Please review the "User Interface Design Goals" (Section 3) and generate a UI prompt suitable for an AI UI generation tool like v0 or Midjourney. The prompt should capture the essence of the "asset-first," clean, and modern aesthetic, as well as the core components like the chat input, message display, and the optional debug panel.

#### 9.2. Architect Prompt

`*architect` Here is the approved Product Requirements Document (PRD). Please use it to create a comprehensive Architecture document. Pay close attention to the "Technical Assumptions" (Section 4) and the two-epic structure, ensuring your architecture supports the real-time, streaming-first approach using WebSockets as defined in the epics.
