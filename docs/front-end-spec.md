### **Front-End Specification: Huge IFX Soccer AI Demo**

**Objective:** To provide a clear and comprehensive specification for the front-end of the Huge IFX Soccer AI Demo, based on the approved Product Requirements Document (PRD).

---

#### **1. Overall UX Vision & Principles**

*   **UX Vision:** The user experience will be clean, modern, and "asset-first." The primary focus will be on the visual content (player images, team logos), with the conversational text acting as a supportive layer. The interface should feel premium, responsive, and immediately engaging, aligning with Huge's reputation for high-quality design.
*   **Key Principles:**
    *   **Asset-First:** The visual content is the star of the show.
    *   **Conversational:** Interaction is natural and chat-like.
    *   **Progressive Disclosure:** Information is revealed contextually to avoid overwhelming the user.
    *   **Responsive:** The experience is seamless across all devices.

---

#### **2. Core Screens & Views**

*   **Main Chat/Search View:**
    *   **Description:** The primary interface for user interaction. It will feature a conversation history, a text input field with a "Send" button, and a display area for returned assets. The asset display area will be fixed, ensuring the visual content is always visible while the conversational text can scroll and stream.
    *   **Components:**
        *   Conversation history display (scrollable).
        *   Fixed asset display area.
        *   Text input field (`shadcn/ui` Input).
        *   Send button (`shadcn/ui` Button).
*   **Asset Detail View (Modal):**
    *   **Description:** A modal that appears when a user clicks on a returned asset. It will display a larger version of the asset along with key attributes and stats.
    *   **Components:**
        *   Large asset image.
        *   Key-value pairs for attributes/stats.
        *   Close button.
*   **Status Bubbles / Toasts:**
    *   **Description:** To provide real-time feedback on system status and errors, the front-end will display status bubbles (also known as "toasts"). These will appear in the top-right corner of the screen and will automatically fade after a short period.
    *   **Trigger:** The backend will emit "status" messages via the WebSocket connection, which will trigger the display of these bubbles on the front-end.
    *   **Example:** A "status" message could indicate that the system is "Searching for players..." or could display an error message if something goes wrong.
*   **Developer/Debug Panel:**
    *   **Description:** An optional, toggleable panel to display underlying I/O for demonstration purposes (e.g., LLM prompts, vector search results).
    *   **Settings Area:** A section within the debug panel for managing session-specific settings. This should include, but is not limited to, fields for `zep`, `freeplay`, `email`, `first name`, and `last name`.

---

#### **3. Component Library & Styling**

*   **Component Library:** `shadcn/ui` will be used for all UI components to ensure a consistent and high-quality look and feel.
*   **Styling:** A clean, sophisticated aesthetic will be implemented. Specific brand guidelines will be incorporated once provided.

---

#### **4. Accessibility**

*   **Standard:** A best-effort approach to accessibility will be taken.
*   **Implementation:** We will leverage the built-in accessibility features of the `shadcn/ui` component library.

---

#### **5. Responsiveness & Target Platforms**

*   **Target Devices:** The application will be fully responsive and designed to work flawlessly on desktop, tablet, and mobile devices.
*   **Target Platforms:** Modern web browsers.

---

### **6. Implementation Details**

*   **Framework:** The project was initialized as a Next.js application using the App Router.
*   **UI Components:** The UI is built with `shadcn/ui` components, which provides a solid foundation of accessible and composable components.
*   **Containerization:** The application is containerized using Docker. A `Dockerfile` is provided in the `ifx-app` directory, and a service has been added to the `docker-compose.yaml` file to manage the application container.
*   **Component Structure:** The UI has been broken down into the following reusable components, located in the `ifx-app/src/components` directory:
    *   `AssetDisplay`: Renders the fixed asset on the left side of the screen.
    *   `ChatHistory`: Renders the scrollable chat history.
    *   `ChatInput`: Renders the chat input field and send button.
    *   `DevPanel`: Renders the collapsible dev/debug panel with a settings area and a toast trigger.
*   **Layout:** The main layout is a two-panel design with a fixed left panel for the asset and a scrollable right panel for the chat. This is achieved using Flexbox and CSS positioning.
*   **Status Notifications:** The application includes a "toast" notification system using `shadcn/ui`'s `Toaster` component. This allows the backend to send real-time status updates to the user.
