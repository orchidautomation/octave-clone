# AgentOS Implementation Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [Core Components](#core-components)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Security & Middleware](#security--middleware)
8. [Advanced Features](#advanced-features)
9. [Deployment](#deployment)
10. [Integration Examples](#integration-examples)
11. [Performance & Benchmarks](#performance--benchmarks)

---

## Overview

### What is AgentOS?

AgentOS is a high-performance, production-ready runtime for multi-agent systems built by Agno. It provides:

- **FastAPI-based Runtime**: Pre-built infrastructure for agent orchestration
- **Privacy-First Design**: Runs entirely in your cloud with zero external data transmission
- **Integrated Control Plane**: Browser-based UI for real-time monitoring and management
- **Multi-Agent Coordination**: Support for agents, teams, and workflows
- **Model Agnostic**: Works with any LLM provider (OpenAI, Anthropic, etc.)

### Key Value Propositions

1. **Speed**: 3μs agent instantiation (529× faster than LangGraph)
2. **Privacy**: Complete data control with no external dependencies
3. **Scale**: Async-first, stateless, horizontally scalable architecture
4. **Developer Experience**: Type-safe, production-ready from day one

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      AgentOS Control Plane                  │
│                   (Browser-based UI)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ Direct Connection
┌────────────────────────▼────────────────────────────────────┐
│                    AgentOS Runtime                          │
│                   (FastAPI Application)                     │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │   Agents     │    Teams     │  Workflows   │            │
│  └──────┬───────┴──────┬───────┴──────┬───────┘            │
│         │              │              │                     │
│  ┌──────▼──────────────▼──────────────▼───────┐            │
│  │         Knowledge & Memory Layer          │            │
│  │  (Vector DBs, Session State, User Memory)  │            │
│  └───────────────────────────────────────────┘            │
│                                                             │
│  ┌──────────────────────────────────────────┐              │
│  │       External Integrations              │              │
│  │  (MCP, Slack, WhatsApp, Custom Tools)    │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   Your Infrastructure │
              │  (PostgreSQL, SQLite, │
              │   Vector Stores, etc) │
              └──────────────────────┘
```

### Core Concepts

**Agents**: Individual AI entities that:
- Process messages using specified LLM models
- Maintain conversation history in databases
- Access tools and execute actions
- Store session data and user memories

**Teams**: Multi-agent collaborative systems where:
- A leader agent coordinates member agents
- Tasks are delegated based on capabilities
- Shared context is maintained across agents
- Responses are synthesized collectively

**Workflows**: Orchestrated step-based execution with:
- Sequential, parallel, looped, or conditional flows
- Steps can be agents, teams, or Python functions
- Shared state management across components
- Controlled execution with rollback capabilities

---

## Getting Started

### Installation

```bash
pip install agno
```

### Minimal AgentOS Setup

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.os import AgentOS

# Create an agent
assistant = Agent(
    name="Assistant",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=["You are a helpful AI assistant."],
    markdown=True,
)

# Initialize AgentOS
agent_os = AgentOS(
    id="my-first-os",
    description="My first AgentOS",
    agents=[assistant],
)

# Get FastAPI app
app = agent_os.get_app()

# Serve (development)
if __name__ == "__main__":
    agent_os.serve(app="my_os:app", reload=True)
```

**Access**: Navigate to `http://localhost:7777` (default port)

### AgentOS with Claude & Persistent Storage

```python
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.os import AgentOS
from agno.tools.mcp import MCPTools

# Create agent with database and tools
agno_agent = Agent(
    name="Agno Agent",
    model=Claude(id="claude-sonnet-4-5"),
    db=SqliteDb(db_file="agno.db"),
    tools=[
        MCPTools(
            transport="streamable-http",
            url="https://docs.agno.com/mcp"
        )
    ],
    add_history_to_context=True,
    markdown=True,
)

# Initialize AgentOS
agent_os = AgentOS(agents=[agno_agent])
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="agno_agent:app", reload=True)
```

---

## Core Components

### 1. Agents

#### Basic Agent Configuration

```python
from agno.agent import Agent
from agno.models.anthropic import Claude

agent = Agent(
    name="Research Assistant",
    model=Claude(id="claude-sonnet-4-5"),
    instructions=[
        "You are a research assistant specialized in technical documentation.",
        "Always cite your sources.",
        "Provide detailed, accurate information."
    ],
    markdown=True,
    add_history_to_context=True,
    num_history_responses=5,
)
```

#### Agent with Tools

```python
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.filesystem import FileSystemTools

agent = Agent(
    name="Search Agent",
    model=Claude(id="claude-sonnet-4-5"),
    tools=[
        DuckDuckGoTools(),
        FileSystemTools(),
    ],
)
```

#### Agent with Memory

```python
from agno.memory.db.postgres import PgMemoryDb

agent = Agent(
    name="Memory Agent",
    model=Claude(id="claude-sonnet-4-5"),
    memory=PgMemoryDb(
        db_url="postgresql://user:password@localhost:5432/agno_db",
        table_name="user_memories",
    ),
    add_history_to_context=True,
)
```

### 2. Teams

```python
from agno.team import Team

# Create team members
researcher = Agent(
    name="Researcher",
    role="Research and gather information",
    model=Claude(id="claude-sonnet-4-5"),
)

writer = Agent(
    name="Writer",
    role="Write and format content",
    model=Claude(id="claude-sonnet-4-5"),
)

# Create team with leader
research_team = Team(
    name="Research Team",
    agents=[researcher, writer],
    leader=researcher,
    instructions=[
        "Collaborate to produce high-quality research reports.",
        "Researcher gathers information, Writer formats the final output."
    ],
)

# Add to AgentOS
agent_os = AgentOS(teams=[research_team])
```

### 3. Workflows

```python
from agno.workflow import Workflow, Task
from agno.agent import Agent

# Define workflow steps
def validate_input(state: dict) -> dict:
    """Validate user input"""
    state['validated'] = True
    return state

analyze_agent = Agent(
    name="Analyzer",
    model=Claude(id="claude-sonnet-4-5"),
)

# Create workflow
workflow = Workflow(
    name="Analysis Workflow",
    tasks=[
        Task(function=validate_input),
        Task(agent=analyze_agent),
    ],
)

# Add to AgentOS
agent_os = AgentOS(workflows=[workflow])
```

### 4. Knowledge Management

```python
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.search import SearchType

# Create knowledge base
knowledge = Knowledge(
    vector_db=PgVector(
        db_url="postgresql://user:password@localhost:5432/agno_db",
        table_name="agno_knowledge_vectors",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)

# Add to AgentOS
agent_os = AgentOS(
    agents=[agent],
    knowledge=[knowledge],
)
```

**Supported Content Types**:
- Files: PDF, CSV, JSON, TXT, DOC, DOCX
- Web: URLs and direct file links
- Text: Direct content input

---

## API Reference

### Running Agents

**Endpoint**: `POST /agents/{agent_id}/runs`

**Request**:
```bash
curl 'http://localhost:7777/agents/assistant/runs' \
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'message=Hello, how are you?' \
    --data-urlencode 'stream=True' \
    --data-urlencode 'user_id=john@example.com' \
    --data-urlencode 'session_id=session_123'
```

**Response** (Server-Sent Events):
```
event: message
data: {"content": "Hello! I'm doing well...", "role": "assistant"}

event: done
data: {"run_id": "run_abc123", "status": "completed"}
```

### Running Teams

**Endpoint**: `POST /teams/{team_id}/runs`

**Request**:
```bash
curl 'http://localhost:7777/teams/research-team/runs' \
    --header 'Content-Type: application/json' \
    --data '{
        "message": "Research AI safety trends",
        "user_id": "john@example.com",
        "session_id": "session_456"
    }'
```

### Running Workflows

**Endpoint**: `POST /workflows/{workflow_id}/runs`

**Request**:
```bash
curl 'http://localhost:7777/workflows/analysis-workflow/runs' \
    --header 'Content-Type: application/json' \
    --data '{
        "input_data": {"text": "Analyze this content"},
        "user_id": "john@example.com"
    }'
```

### Cancelling Runs

**Endpoint**: `POST /agents/{agent_id}/runs/{run_id}/cancel`

```bash
curl -X POST 'http://localhost:7777/agents/assistant/runs/run_abc123/cancel'
```

### Configuration Endpoint

**Endpoint**: `GET /config`

Retrieves complete AgentOS configuration including:
- Registered agents, teams, workflows
- Database configurations
- Knowledge bases
- Feature settings

```bash
curl 'http://localhost:7777/config'
```

### Knowledge Management Endpoints

**Add Content to Knowledge Base**:
- `POST /knowledge/{knowledge_id}/documents` - Upload files
- `POST /knowledge/{knowledge_id}/urls` - Add URLs
- `POST /knowledge/{knowledge_id}/text` - Add text content

**Search Knowledge**:
- `POST /knowledge/{knowledge_id}/search` - Hybrid search

### Memory Endpoints

**User Memory**:
- `GET /memory/users/{user_id}` - Get user memories
- `POST /memory/users/{user_id}` - Add user memory
- `DELETE /memory/users/{user_id}/{memory_id}` - Delete memory

### Session Management

**Session History**:
- `GET /sessions/{session_id}` - Get session details
- `GET /sessions/{session_id}/messages` - Get session messages
- `DELETE /sessions/{session_id}` - Clear session

---

## Configuration

### YAML Configuration

Create `agno_config.yaml`:

```yaml
# Chat interface settings
chat:
  quick_prompts:
    assistant:
      - "What can you do?"
      - "Help me with Python code"
    research-team:
      - "Research latest AI trends"
      - "Summarize this paper"

# Memory database configuration
memory:
  dbs:
    - db_id: main-memory-db
      domain_config:
        display_name: "Main User Memories"
        description: "Persistent user context and preferences"

# Knowledge base configuration
knowledge:
  - kb_id: docs-kb
    domain_config:
      display_name: "Documentation Knowledge"
      description: "Company documentation and guides"

# Feature flags
features:
  enable_knowledge_search: true
  enable_user_memory: true
  enable_session_tracking: true
```

**Load Configuration**:

```python
from agno.os import AgentOS

agent_os = AgentOS(
    agents=[agent],
    config="agno_config.yaml"
)
```

### Programmatic Configuration

```python
from agno.os.config import AgentOSConfig, ChatConfig, MemoryConfig

config = AgentOSConfig(
    chat=ChatConfig(
        quick_prompts={
            "assistant": [
                "What can you do?",
                "Help me with Python code"
            ]
        }
    ),
    memory=MemoryConfig(
        dbs=[{
            "db_id": "main-memory-db",
            "domain_config": {
                "display_name": "Main User Memories"
            }
        }]
    )
)

agent_os = AgentOS(
    agents=[agent],
    config=config
)
```

---

## Security & Middleware

### JWT Authentication

```python
from agno.os.middleware import JWTMiddleware
from fastapi import FastAPI

app = agent_os.get_app()

# Add JWT middleware
app.add_middleware(
    JWTMiddleware,
    secret_key="your-jwt-secret-key",
    algorithm="HS256",
    user_id_claim="sub",
    session_id_claim="session_id",
    validate=True,
    exclude_paths=["/health", "/docs"],  # Public routes
)
```

**Token Sources**:
1. **Authorization Header**: `Authorization: Bearer <token>`
2. **HTTP-only Cookie**: `agno_token=<token>`
3. **Priority**: Header takes precedence over cookie

**Token Payload Example**:
```json
{
    "sub": "user_12345",
    "session_id": "session_abc",
    "exp": 1735689600
}
```

### Rate Limiting Middleware

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()

        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < 60
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        self.requests[client_ip].append(now)
        response = await call_next(request)
        return response

# Add to AgentOS
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
```

### Request Logging Middleware

```python
import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        logger.info(
            f"Response: {response.status_code} "
            f"Duration: {duration:.2f}s"
        )
        return response

app.add_middleware(RequestLoggingMiddleware)
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Advanced Features

### Custom FastAPI Integration

Bring your own FastAPI app and integrate AgentOS:

```python
from fastapi import FastAPI, Depends
from agno.os import AgentOS

# Your existing FastAPI app
app = FastAPI(title="My Custom App")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/custom-route")
async def custom_endpoint():
    return {"message": "Custom functionality"}

# Initialize AgentOS with your app
agent_os = AgentOS(
    agents=[agent],
    base_app=app,
    on_route_conflict="preserve_base_app",  # Your routes take precedence
)

# Get the combined app
app = agent_os.get_app()
```

### Custom Routers

Organize endpoints using FastAPI routers:

```python
from fastapi import APIRouter

# Analytics router
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])

@analytics_router.get("/stats")
async def get_stats():
    return {"total_runs": 1000, "active_sessions": 42}

# Include router in app
app.include_router(analytics_router)

# Then initialize AgentOS
agent_os = AgentOS(agents=[agent], base_app=app)
app = agent_os.get_app()
```

### Custom Lifespan Management

Manage startup and shutdown logic:

```python
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):
    # Startup logic
    logger.info("Starting AgentOS...")
    # Initialize connections, load models, etc.

    yield  # Application runs

    # Shutdown logic
    logger.info("Shutting down AgentOS...")
    # Close connections, cleanup resources, etc.

agent_os = AgentOS(
    agents=[agent],
    lifespan=lifespan,
)
```

### MCP Server Integration

Enable Model Context Protocol server:

```python
agent_os = AgentOS(
    agents=[agent],
    enable_mcp_server=True,  # Available at /mcp endpoint
)
```

MCP allows agents to expose their capabilities as tools to other agents.

### Interfaces (Agent Exposure)

#### A2A (Agent-to-Agent Protocol)

```python
from agno.os.interfaces.a2a import A2A

agent_os = AgentOS(
    agents=[agent],
    a2a_interface=True,
)
```

Enables agents to communicate with each other using standardized protocol.

#### AG-UI (Agent-User Interaction)

```python
from agno.os.interfaces.agui import AGUI

chat_agent = Agent(name="Chat", model=Claude(id="claude-sonnet-4-5"))

agent_os = AgentOS(
    agents=[chat_agent],
    interfaces=[AGUI(agent=chat_agent)]
)
```

Provides web-based chat interface for agent interaction.

#### Slack Integration

```python
from agno.os.interfaces.slack import Slack
import os

slack_agent = Agent(
    name="Slack Bot",
    model=Claude(id="claude-sonnet-4-5"),
)

agent_os = AgentOS(
    agents=[slack_agent],
    interfaces=[
        Slack(
            agent=slack_agent,
            bot_token=os.getenv("SLACK_BOT_TOKEN"),
            signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
        )
    ],
)
```

**Required Slack Scopes**:
- `chat:write`
- `app_mentions:read`
- `im:history`
- `channels:history`

#### WhatsApp Integration

```python
from agno.os.interfaces.whatsapp import Whatsapp

whatsapp_agent = Agent(
    name="WhatsApp Assistant",
    model=Claude(id="claude-sonnet-4-5"),
)

agent_os = AgentOS(
    agents=[whatsapp_agent],
    interfaces=[
        Whatsapp(
            agent=whatsapp_agent,
            verify_token=os.getenv("WHATSAPP_VERIFY_TOKEN"),
            access_token=os.getenv("WHATSAPP_ACCESS_TOKEN"),
        )
    ],
)
```

Requires Meta WhatsApp Business API setup.

---

## Deployment

### Development

```bash
# Using agno.serve()
python main.py

# Using uvicorn directly
uvicorn main:app --reload --port 7777
```

### Production

#### Uvicorn (Single Process)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Gunicorn with Uvicorn Workers

```bash
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keep-alive 5
```

#### FastAPI CLI

```bash
fastapi run main.py --host 0.0.0.0 --port 8000
```

### Docker Deployment

**Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**requirements.txt**:
```
agno>=2.0.0
uvicorn[standard]>=0.27.0
gunicorn>=21.2.0
python-multipart>=0.0.6
```

**Build and Run**:

```bash
docker build -t agentos-app .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=your-key agentos-app
```

### Environment Variables

```bash
# API Keys
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# Database
export DATABASE_URL="postgresql://user:password@localhost:5432/agno_db"

# Telemetry (disable for production)
export AGNO_TELEMETRY=false

# AgentOS Settings
export AGENTOS_PORT=7777
export AGENTOS_HOST=0.0.0.0
```

### Cloud Deployment Examples

#### AWS (ECS/Fargate)

1. Build and push Docker image to ECR
2. Create ECS task definition with environment variables
3. Deploy as Fargate service with load balancer
4. Use RDS for PostgreSQL database
5. Store API keys in AWS Secrets Manager

#### Google Cloud (Cloud Run)

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/agentos
gcloud run deploy agentos \
    --image gcr.io/PROJECT_ID/agentos \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars ANTHROPIC_API_KEY=secret:anthropic-key:latest
```

#### Azure (Container Apps)

```bash
az containerapp up \
    --name agentos \
    --resource-group myResourceGroup \
    --location eastus \
    --image myregistry.azurecr.io/agentos:latest \
    --target-port 8000 \
    --ingress external \
    --env-vars ANTHROPIC_API_KEY=secretref:anthropic-key
```

---

## Integration Examples

### Complete Multi-Agent System

```python
from agno.agent import Agent
from agno.team import Team
from agno.workflow import Workflow, Task
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.db.postgres import PgDb
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.openai import OpenAIEmbedder
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.os import AgentOS
import os

# Database configuration
db_url = os.getenv("DATABASE_URL")

# Create specialized agents
researcher = Agent(
    name="Researcher",
    role="Research and gather information from the web",
    model=Claude(id="claude-sonnet-4-5"),
    tools=[DuckDuckGoTools()],
    db=PgDb(db_url=db_url, table_name="researcher_sessions"),
    instructions=[
        "Search for accurate, recent information",
        "Cite all sources",
        "Verify facts from multiple sources"
    ],
)

analyst = Agent(
    name="Analyst",
    role="Analyze data and provide insights",
    model=OpenAIChat(id="gpt-4o"),
    db=PgDb(db_url=db_url, table_name="analyst_sessions"),
    instructions=[
        "Provide detailed analysis",
        "Use data-driven reasoning",
        "Identify patterns and trends"
    ],
)

writer = Agent(
    name="Writer",
    role="Write professional reports and documentation",
    model=Claude(id="claude-sonnet-4-5"),
    db=PgDb(db_url=db_url, table_name="writer_sessions"),
    instructions=[
        "Write clear, concise content",
        "Use professional tone",
        "Structure information logically"
    ],
)

# Create research team
research_team = Team(
    name="Research Team",
    agents=[researcher, analyst, writer],
    leader=researcher,
    instructions=[
        "Collaborate to produce comprehensive research reports",
        "Researcher gathers information",
        "Analyst provides insights",
        "Writer creates final report"
    ],
)

# Create customer support agent
support_agent = Agent(
    name="Support Agent",
    model=Claude(id="claude-sonnet-4-5"),
    db=PgDb(db_url=db_url, table_name="support_sessions"),
    instructions=[
        "Be helpful and empathetic",
        "Provide accurate information",
        "Escalate complex issues when needed"
    ],
)

# Create knowledge base
docs_knowledge = Knowledge(
    vector_db=PgVector(
        db_url=db_url,
        table_name="docs_vectors",
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)

# Create workflow
def validate_request(state: dict) -> dict:
    """Validate incoming request"""
    if not state.get('message'):
        raise ValueError("Message is required")
    state['validated'] = True
    return state

def route_request(state: dict) -> dict:
    """Route to appropriate agent"""
    message = state['message'].lower()
    if 'research' in message or 'analyze' in message:
        state['route'] = 'research_team'
    else:
        state['route'] = 'support'
    return state

support_workflow = Workflow(
    name="Support Workflow",
    tasks=[
        Task(function=validate_request),
        Task(function=route_request),
    ],
)

# Initialize AgentOS
agent_os = AgentOS(
    id="production-os",
    description="Multi-agent production system",
    agents=[support_agent],
    teams=[research_team],
    workflows=[support_workflow],
    knowledge=[docs_knowledge],
    config="config.yaml",
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="main:app", reload=True)
```

### E-commerce Support System

```python
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.postgres import PgDb
from agno.memory.db.postgres import PgMemoryDb
from agno.tools.python import PythonTools
from agno.os import AgentOS

db_url = os.getenv("DATABASE_URL")

# Order tracking agent
order_agent = Agent(
    name="Order Tracker",
    model=Claude(id="claude-sonnet-4-5"),
    tools=[PythonTools()],
    db=PgDb(db_url=db_url, table_name="order_sessions"),
    memory=PgMemoryDb(db_url=db_url, table_name="customer_memory"),
    instructions=[
        "Help customers track their orders",
        "Provide shipping updates",
        "Remember customer preferences and past orders"
    ],
)

# Product recommendation agent
recommendation_agent = Agent(
    name="Recommender",
    model=Claude(id="claude-sonnet-4-5"),
    db=PgDb(db_url=db_url, table_name="recommendation_sessions"),
    memory=PgMemoryDb(db_url=db_url, table_name="customer_memory"),
    instructions=[
        "Recommend products based on customer preferences",
        "Use purchase history to personalize suggestions",
        "Explain why products are recommended"
    ],
)

# Initialize AgentOS
ecommerce_os = AgentOS(
    id="ecommerce-os",
    agents=[order_agent, recommendation_agent],
)

app = ecommerce_os.get_app()
```

---

## Performance & Benchmarks

### Official Benchmarks (October 2025)

Tested on Apple M4 MacBook Pro:

| Metric | Agno | LangGraph | PydanticAI | CrewAI |
|--------|------|-----------|------------|--------|
| **Agent Instantiation** | 3 μs | 1,587 μs | 171 μs | 210 μs |
| **Speed vs Agno** | 1× | 529× slower | 57× slower | 70× slower |
| **Memory per Agent** | 6.6 KB | 158.7 KB | 26.4 KB | 66.2 KB |
| **Memory vs Agno** | 1× | 24× more | 4× more | 10× more |

### Performance Characteristics

**Async-First Design**:
- Non-blocking I/O operations
- Concurrent request handling
- Minimal memory footprint per agent

**Stateless Architecture**:
- No in-memory session state
- Horizontal scaling without session stickiness
- Database-backed persistence

**Optimized Runtime**:
- 3 microsecond agent instantiation
- Lazy loading of models and tools
- Efficient memory management

### Scaling Recommendations

**Single Instance**:
- 4-8 CPU cores
- 8-16 GB RAM
- Handles 100-500 concurrent requests

**Horizontal Scaling**:
- Load balancer (ALB/NLB)
- Multiple AgentOS instances
- Shared PostgreSQL database
- Redis for distributed caching (optional)

**Database Optimization**:
- Connection pooling (pgbouncer)
- Read replicas for analytics
- Separate databases for sessions, memory, knowledge

---

## Connecting to AgentOS Control Plane

### Local Development

1. Access AgentOS UI at platform
2. Navigate to team/organization settings
3. Click "+" to add new OS instance
4. Select **Local** environment
5. Configure endpoint: `http://localhost:7777`
6. Name your instance (e.g., "Dev OS")
7. Add optional tags for organization
8. Click **CONNECT**

### Production Deployment

1. Access AgentOS UI
2. Click "+" to add new OS
3. Select **Live** environment
4. Enter production endpoint (e.g., `https://api.yourdomain.com`)
5. Configure authentication if using JWT/bearer tokens
6. Name your instance (e.g., "Production OS")
7. Add tags: `production`, `v1.0.0`, etc.
8. Click **CONNECT**

### Control Plane Features

- **Chat Interface**: Test agents, teams, workflows
- **Knowledge Management**: Upload documents, manage content
- **Memory Browser**: View and edit user memories
- **Session Tracking**: Monitor conversation history
- **Analytics**: View usage metrics and performance
- **User Management**: Control access with RBAC
- **OS Switching**: Toggle between multiple environments

---

## Best Practices

### Security

1. **API Keys**: Use environment variables, never hardcode
2. **JWT Tokens**: Implement with short expiration times
3. **Rate Limiting**: Protect against abuse
4. **CORS**: Restrict to known origins
5. **HTTPS**: Always use TLS in production
6. **Input Validation**: Sanitize all user inputs

### Performance

1. **Database Indexes**: Index session_id, user_id, timestamps
2. **Connection Pooling**: Use pgbouncer or SQLAlchemy pools
3. **Caching**: Cache knowledge base queries
4. **Async Operations**: Use async/await throughout
5. **Monitoring**: Track response times, error rates

### Development Workflow

1. **Local Development**: Use SQLite for quick iteration
2. **Testing**: Use separate test databases
3. **Staging**: Mirror production configuration
4. **Production**: Use managed PostgreSQL services
5. **Telemetry**: Disable in production (`AGNO_TELEMETRY=false`)

### Agent Design

1. **Single Responsibility**: Each agent has clear purpose
2. **Clear Instructions**: Provide specific, detailed instructions
3. **Tool Selection**: Only include necessary tools
4. **Memory Management**: Use user memory for personalization
5. **Error Handling**: Implement graceful degradation

---

## Troubleshooting

### Common Issues

**Agent not responding**:
- Check API keys in environment variables
- Verify model ID is correct
- Review agent logs for errors

**Database connection errors**:
- Verify DATABASE_URL format
- Check database is accessible
- Confirm credentials are correct

**Control Plane connection failed**:
- Ensure AgentOS is running
- Check firewall/network settings
- Verify endpoint URL is correct

**High memory usage**:
- Limit `num_history_responses`
- Use database-backed memory instead of in-memory
- Monitor agent instantiation patterns

### Debug Mode

```python
import logging

logging.basicConfig(level=logging.DEBUG)

agent_os = AgentOS(
    agents=[agent],
    debug=True,  # Enable debug mode
)
```

---

## Resources

- **Official Documentation**: https://docs.agno.com
- **GitHub Repository**: https://github.com/agno-agi/agno
- **Examples**: https://docs.agno.com/examples
- **Community Forum**: https://community.agno.com
- **Discord**: https://discord.gg/4MtYHHrgA8
- **Full Documentation (LLM)**: https://docs.agno.com/llms-full.txt

---

## License

AgentOS is part of the Agno framework, licensed under Apache-2.0.

---

**Last Updated**: November 2025
**AgentOS Version**: 2.0+
**Documentation Version**: 1.0
