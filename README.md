# SelfHealOps

> **An autonomous, self-healing DevOps pipeline agent designed to automatically classify, analyze, and remediate CI/CD pipeline failures and infrastructure issues using a hierarchical multi-agent system.**

---

## Overview

SelfHealOps operates as a LangGraph-powered state machine utilizing specialized AI agents to process incident data, determine root causes via NVIDIA NIM integration, generate concrete remediation plans, and execute safe fixes through a strict policy engine. 

This project serves as a reference implementation for:
*   LangGraph-based State Machine Orchestration
*   Autonomous CI/CD Remediation Pipelines
*   Hierarchical AI Agent Delegation
*   Production-grade Observability and Policy Enforcement

---

## System Architecture

The system creates a directed cyclic graph of agent execution, managed by a LangGraph orchestrator.

### High-Level Design

```mermaid
graph TD
    START --> collect_evidence
    collect_evidence --> classify_failure
    classify_failure --> analyze_root_cause
    analyze_root_cause --> plan_remediation
    plan_remediation --> validate_safety
    
    validate_safety -- Safe --> execute_action
    validate_safety -- Unsafe --> escalate
    
    execute_action --> validate_fix
    
    validate_fix -- Passed --> extract_learning
    validate_fix -- Failed (under retry limit) --> plan_remediation
    validate_fix -- Failed (limit reached) --> escalate
    
    extract_learning --> END
    escalate --> END
```

---

## Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Core Logic** | Python 3.12+ | Type-hinted, asynchronous FastAPI backend. |
| **LLM Provider** | NVIDIA NIM | High-performance inference endpoints powering Langchain workflows. |
| **Orchestration** | LangGraph | State management and cyclical workflow engine. |
| **Database** | PostgreSQL | Asynchronous SQLAlchemy ORM for relational tracking. |
| **Caching & Vectors**| Redis | Caching and Semantic Vector Search (Langchain). |
| **Observability** | Prometheus & Grafana | Real-time metrics and latency monitoring. |
| **Integrations** | PyGithub & K8s Client | External execution vectors for pipeline healing. |

---

## Agent Personas

The system splits the cognitive and operational load across specialized worker agents:

### 1. The Classifier (FailureClassificationAgent)
*   **Role:** Analyzes incoming CI/CD logs and pipeline context to categorize the exact failure domain (e.g., DEPENDENCY_FAILURE, INFRASTRUCTURE_FAILURE).

### 2. The Analyst (RootCauseAnalysisAgent)
*   **Role:** Performs deep analysis of historical commits and error tracebacks to determine the true technical root cause.

### 3. The Strategist (RemediationPlanningAgent)
*   **Role:** Translates the root cause into a sequential list of deterministic actions required to fix the system.

### 4. The Auditor (SafetyValidationAgent)
*   **Role:** Evaluates the proposed action plan against rigid policy guardrails to prevent destructive commands.

### 5. The Scholar (LearningAgent)
*   **Role:** Extracts successful remediation patterns and stores them semantically, enabling future incidents to be resolved instantly via memory recall.

---

## Getting Started

### Prerequisites
- Python 3.12+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### 1. Environment Configuration
Create a `.env` file in the root directory:

```ini
PROJECT_NAME="SelfHealOps API"
API_V1_STR="/api/v1"
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/selfhealops"
REDIS_HOST="localhost"
REDIS_PORT="6379"
SECRET_KEY="your-secure-random-secret-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES="30"
GITHUB_TOKEN="your-github-personal-access-token"
GITHUB_WEBHOOK_SECRET="your-github-webhook-secret"
NVIDIA_API_KEY="your-nvidia-nim-api-key"
```

### 2. Startup Procedures
Start the infrastructure:
```bash
docker-compose up -d
```

Setup the Python environment and database:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

Run the application:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive API Docs available at `http://localhost:8000/docs`.

---

## Project Structure

```text
SelfHealOps/
├── backend/                    # Core Python Application
│   ├── agents/                 # Specialized LangGraph AI Agents
│   ├── api/                    # FastAPI Routers and Endpoints
│   ├── core/                   # Security, Metrics, and Configs
│   ├── database/               # Async Session and Repositories
│   ├── models/                 # SQLAlchemy ORM Models
│   ├── schemas/                # Pydantic Output Validators
│   ├── services/               # GitHub, K8s, and NIM Integrations
│   └── workflows/              # LangGraph State Machine
├── docs/                       # Architectural and Security Manuals
├── infrastructure/             # Prometheus, Grafana, K8s Manifests
├── migrations/                 # Alembic Database Migrations
└── tests/                      # Pytest Suites
```

---

## Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| Database Connection Refused | Docker not running | Ensure `docker-compose up -d` was executed successfully. |
| 401 Unauthorized | Missing JWT | Authenticate via `/api/v1/auth/login` to receive a Bearer token. |
| Validation Error | Bad LLM Output | The system will auto-retry. Check `NVIDIA_API_KEY` limits. |
| ModuleNotFoundError | Missing Env | Ensure the `venv` is activated before running `uvicorn`. |

---

## License

Distributed under the MIT License. See LICENSE for more details.

**Maintained by [amitdevx](https://github.com/amitdevx)**  
Website: [amitdevx](https://amitdevx.tech)
