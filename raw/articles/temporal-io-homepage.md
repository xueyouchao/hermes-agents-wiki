# Temporal: Durable Execution for Developers

Source: https://temporal.io/
Retrieved: 2026-04-16

## Core Concept: Durable Execution
Temporal is an open-source platform that enables **Durable Execution**, allowing developers to build applications that maintain state and recover automatically from failures in distributed systems.

*   **Automatic Recovery:** Workflows pick up exactly where they left off after a failure.
*   **No Manual Recovery:** Eliminates the need for complex reconciliation logic or manual intervention.
*   **Visibility:** Provides full insight into the exact state of every execution, replacing the need to sift through logs.

## Key Technical Components
*   **SDKs:** Native support for **Python, Go, TypeScript, Ruby, C#, Java, and PHP**.
*   **Workflows:** Durable, fault-tolerant code that handles business logic (e.g., order processing, AI model training).
*   **Activities:** Functions designed to handle failure-prone logic (like third-party APIs) with built-in automatic retries.
*   **Temporal Service:** The backend that persists application state, manages task queues, signals, and timers.

## Common Use Cases
*   **AI & Agents:** Reliable MCP (Model Context Protocol) and orchestration for training pipelines.
*   **Human-in-the-Loop:** Durable orchestration for workflows requiring human input.
*   **Financial Services:** Durable ledgers for transaction tracking and "Saga" patterns for compensating transactions.
*   **Infrastructure:** CI/CD pipelines, cloud deployment, and fleet management.
*   **Business Operations:** Order fulfillment and customer acquisition/onboarding.

## Deployment Options
1.  **Self-Hosted:** 100% Open Source (MIT-licensed).
2.  **Temporal Cloud:** A managed service offering. *Note: Temporal never sees your code in either deployment model.*
    *   **Offer:** New users can get **$1,000 in free credits** for Temporal Cloud.

## Industry Validation
Temporal is used by global enterprises including **OpenAI, NVIDIA, Salesforce, Netflix, Snap, Cloudflare, and Doordash.**

### Key Quotes
> "Temporal does to backend and infra, what React did to frontend… the surface exposed to the developer is a beautiful 'render()' function to organize your backend workflows."
> — **Guillermo Rauch**, Founder & CEO at Vercel

> "Without Temporal's technology, we would've spent a significant amount of time rebuilding Temporal and would've very likely done a worse job."
> — **Mitchell Hashimoto**, Co-founder at Hashicorp

## Events & Resources
*   **Replay Conference:** The Durable Execution conference for developers and AI.
    *   **Date:** May 5–7
    *   **Location:** Moscone Center, San Francisco
    *   **Content:** Workshops, talks, and a hackathon focused on reliable agentic systems.
*   **Open Source Stats:** 19,600+ GitHub Stars.
*   **Heritage:** Built by the creators of AWS SQS, AWS SWF, and Uber's Cadence.