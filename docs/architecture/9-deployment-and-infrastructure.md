# 9. Deployment and Infrastructure

*   **Frontend:** The Next.js frontend will be deployed on Vercel, leveraging its CI/CD capabilities for automatic deployments from the `main` branch.
*   **Backend:** The Dockerized FastAPI backend will be deployed to a container hosting service. Vercel is a possibility, but other services like Google Cloud Run or AWS Fargate are also suitable alternatives.
*   **Monorepo Deployment:** The Vercel project will be configured to correctly build and deploy the frontend and backend from their respective directories within the monorepo.
