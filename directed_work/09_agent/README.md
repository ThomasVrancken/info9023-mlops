# Lab 9 [Sprint 5, W10]: Agentic AI with tool use and RAG

## 0. Introduction

In every lab so far you have built, trained, or deployed ML models. In this lab you build something different. You use an LLM as a reasoning engine that decides which tools to call, inspects the results, and keeps going until it can answer your question. This is an AI agent.

There are several frameworks for building agents. The major LLM providers offer their own SDKs: [Anthropic Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview), [OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents-sdk), and Google's ADK. These give you maximum control but require more boilerplate. In this lab you will use [Agno](https://www.agno.com/), a lightweight framework that works with any model provider and is the simplest way to get started. Agno handles the plumbing (tool dispatch, message history, streaming) so you can focus on choosing the right tools and wiring agents together.

By the end of this lab you will have:
- Built an agent powered by Gemini that can search the web and look up financial data
- Created your own custom tools
- Combined multiple specialist agents into a multi-agent team
- Added a knowledge base with RAG so the agent can answer questions about your own documents
- Deployed the whole thing as an API on Cloud Run

## 1. Background

### 1.1. What is an agent?

A chatbot generates text. An agent generates text **and** takes actions. The three components of an agent are (1) an LLM that reasons about what to do, (2) a set of tools it can call, and (3) a loop that orchestrates the conversation. The LLM reads the user's question, decides whether it needs to call a tool, receives the tool's output, and repeats until it has enough information to answer.

### 1.2. Tool use (function calling)

Each tool is defined by three things: a **name**, a **description** (so the LLM knows when to use it), and an **input schema** that specifies the expected arguments with their types. These definitions are injected into the system prompt. The LLM reads them and decides, based on the user's question, whether it needs to call a tool and which arguments to pass.

When the LLM decides to call a tool, it does not execute anything itself. It returns a structured block containing the tool name and the arguments it chose. Your code (or in this case, the Agno framework) takes that block, calls the actual function, and sends the **output back as text** into the conversation. The LLM then reads that output as additional context and continues reasoning. It may call another tool, or it may decide it has enough information to produce a final answer.

This separation is important. The LLM never runs code, never touches your database, never calls an API directly. It only produces a request. Your code decides whether and how to execute it. The quality of the tool definition matters a lot. If the description is vague, the LLM will not know when to use the tool. If the input schema is wrong, the LLM will pass bad arguments and the function will fail.

### 1.3. Multi-agent systems

Just like in a company, complex problems benefit from specialists who collaborate. A single generalist agent can answer many questions, but it will never match the depth of a dedicated expert. In a multi-agent system, each agent has its own **system prompt**, its own set of **tools**, and optionally its own **model**. Concretely, each agent is a fully independent LLM session with its own instructions and capabilities. A financial analyst agent has a system prompt telling it to interpret stock data and only has finance tools. A research agent has a system prompt focused on web research and only has search tools. They never see each other's tools or instructions.

A team leader (itself an LLM) coordinates them, deciding which specialist should handle each part of a question and combining their answers into a final response. This mirrors how real teams work and produces better results than a single agent trying to do everything.

### 1.4. RAG (Retrieval-Augmented Generation)

LLMs do not know your private data. They were trained on public text and have a knowledge cutoff. RAG solves this by retrieving relevant documents from your own data and injecting them into the prompt.

The pipeline has four steps. (1) Split your documents into small chunks. (2) Convert each chunk into a vector embedding, a numerical representation that captures its meaning. (3) Store the embeddings in a **vector database**. (4) At query time, embed the user's question, find the nearest chunks, and add them to the prompt. The LLM now has the relevant context and can generate a grounded answer.

A vector database (ChromaDB, Pinecone, Weaviate, etc.) is a database optimized for storing and searching embeddings. It is the retrieval engine behind RAG.

### 1.5. The agentic loop

```
User question
     |
     v
 LLM (Gemini)  <-- tool definitions
     |
     v
 tool_use block?
   /        \
  no         yes
  |           |
  v           v
Final      Execute tool
answer     (framework handles this)
              |
              v
         tool result
              |
              v
         LLM (loop back)
```

The loop repeats until the model decides it has enough information to produce a final answer. With Agno, you do not write this loop yourself.

## 2. Prerequisites

1. [uv](https://docs.astral.sh/uv/) installed
2. Docker Desktop installed and running
3. The Google Cloud CLI installed and authenticated

### Gemini via Vertex AI

You will use Gemini through Vertex AI, which means the API calls are billed to your GCP project (your educational credits). There is no separate API key to create.

Enable the required APIs.

```bash
gcloud services enable aiplatform.googleapis.com run.googleapis.com artifactregistry.googleapis.com --project=YOUR_PROJECT_ID
```

Authenticate your local environment so the SDK can call Vertex AI.

```bash
gcloud auth application-default login
```

### Project setup

Initialize a project in this lab's folder and add the dependencies.

```bash
uv init
uv add agno google-genai ddgs yfinance chromadb flask gunicorn
```

The first time you import `chromadb`, it downloads a small embedding model (~100 MB). Trigger this now so it does not slow you down later.

```bash
uv run python -c "import chromadb; chromadb.Client(); print('ChromaDB ready')"
```

This lab uses `gemini-2.5-flash`, a fast and cheap Gemini model. A full lab session should cost very little with your GCP credits.

## 3. Your first agent

Create a file `src/first_agent.py`. This is where you will write all the code for sections 3 and 4.

An Agno `Agent` takes a few key arguments.
- **`model`**: the LLM to use. Here we use Gemini 2.5 Flash through Vertex AI. Replace `YOUR_PROJECT_ID` with your actual GCP project ID.
- **`instructions`**: the system prompt. This is where you tell the agent who it is and how it should behave.
- **`tools`**: a list of tools the agent can call (we will add these in section 4).
- **`markdown`**: when `True`, the agent formats its output as Markdown in the terminal.

`print_response` sends a message to the agent and prints the response. With `stream=True`, the response is printed token by token as it arrives.

```python
from agno.agent import Agent
from agno.models.google import Gemini

agent = Agent(
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    instructions="You are a helpful assistant. Be concise.",
    markdown=True,
)

agent.print_response("What are the three laws of robotics?", stream=True)
```

Run it.

```bash
uv run python src/first_agent.py
```

The agent sends your question to Gemini and streams the response back. No tools yet, so this is just a simple LLM call. The agent becomes useful once we give it tools in the next section.

## 4. Adding tools

Tools are what turn a chatbot into an agent. Agno provides dozens of built-in tools and makes it easy to create your own.

### 4.1. Built-in tools: web search

Add DuckDuckGo search so the agent can look up current information.

```python
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    tools=[DuckDuckGoTools()],
    instructions="You are a research assistant. Search the web when you need current information.",
    markdown=True,
)

agent.print_response("What are the latest developments in AI agents?", stream=True)
```

The agent decides on its own whether to search the web or answer from its training data. Try a question about a recent event to see it call the tool.

### 4.2. Built-in tools: finance

Add YFinance so the agent can look up stock data.

```python
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools

finance_agent = Agent(
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    tools=[YFinanceTools(
        enable_stock_price=True,
        enable_analyst_recommendations=True,
        enable_company_info=True,
        enable_company_news=True,
    )],
    instructions="You are a financial analyst. Look up real data before answering.",
    markdown=True,
)

finance_agent.print_response("How is NVIDIA doing? Give me the stock price and recent news.", stream=True)
```

Agno has many more built-in tools: Wikipedia, arXiv, HackerNews, GitHub, Slack, Google Sheets, and more. Browse the [tools documentation](https://docs.agno.com/tools/toolkits/overview) to see the full list.

### 4.3. Custom tools

You can turn any Python function into a tool. The function name becomes the tool name, and the docstring becomes the description the model reads to decide when to call it. Type annotations on the arguments are mandatory. Agno uses them to generate the input schema that tells the LLM what types to pass (string, float, int, etc.). Without type annotations, the framework cannot build the schema and the tool will not work.

```python
from agno.agent import Agent
from agno.models.google import Gemini

def calculate_compound_interest(principal: float, annual_rate: float, years: int) -> str:
    """Calculate compound interest.

    Args:
        principal: Initial investment amount in dollars.
        annual_rate: Annual interest rate as a percentage (e.g. 5.0 for 5%).
        years: Number of years.

    Returns:
        A summary of the final amount and total interest earned.
    """
    final = principal * (1 + annual_rate / 100) ** years
    interest = final - principal
    return f"Initial: ${principal:,.2f}, Final: ${final:,.2f}, Interest earned: ${interest:,.2f}"

agent = Agent(
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    tools=[calculate_compound_interest],
    instructions="You are a financial advisor. Use the compound interest calculator when needed.",
    markdown=True,
)

agent.print_response("If I invest $10,000 at 7% annual return for 20 years, how much will I have?", stream=True)
```

Put all the code from sections 4.1 through 4.3 into `src/first_agent.py` and run it to verify everything works.

```bash
uv run python src/first_agent.py
```

## 5. Multi-agent teams

As explained in section 1.3, complex questions benefit from specialist agents working together. In Agno, you connect agents through a `Team`. The team has its own LLM (the team leader) whose job is to read the user's question, break it down into subtasks, and delegate each subtask to the right specialist. The team leader sees the names and instructions of its members (but not their tools). Based on that, it decides who should handle what. Once the specialists have answered, the team leader reads their responses and synthesizes a final answer for the user.

Create `src/team.py`.

```python
from agno.agent import Agent
from agno.team import Team
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

web_agent = Agent(
    name="Web Researcher",
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    tools=[DuckDuckGoTools()],
    instructions="You search the web for current information. Return factual, sourced answers.",
)

finance_agent = Agent(
    name="Financial Analyst",
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    tools=[YFinanceTools(
        enable_stock_price=True,
        enable_analyst_recommendations=True,
        enable_company_news=True,
    )],
    instructions="You analyze financial data. Always look up real numbers before answering.",
)

team = Team(
    name="Research Team",
    mode="coordinate",
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    members=[web_agent, finance_agent],
    instructions="You are the team leader. Delegate research to the Web Researcher and financial questions to the Financial Analyst. Synthesize their findings into a final answer.",
    markdown=True,
)

team.print_response(
    "What is the current state of the AI chip market? Include NVIDIA's stock performance and any recent industry news.",
    stream=True,
)
```

Agno supports three team modes.
- **coordinate**: a team leader decides which agent handles which subtask (used above).
- **route**: a router sends the entire query to the single best specialist.
- **collaborate**: all agents see the question and contribute.

Run the team.

```bash
uv run python src/team.py
```

Watch the output. You will see the team leader delegate parts of the question to different agents, each using their own tools.

## 6. Adding a knowledge base (RAG)

Your agent can now search the web and look up finance data. But what about your own private documents? This is where RAG comes in.

The `data/` folder contains four markdown files about MLOps concepts (CI/CD, monitoring, feature stores, experiment tracking). You will load them into a ChromaDB vector database and give the agent a tool to search them.

Create `src/rag_agent.py`.

### 6.1. Load documents into ChromaDB

```python
import os
import chromadb

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="mlops_knowledge")

def load_documents(directory):
    documents = []
    metadatas = []
    ids = []

    for filename in os.listdir(directory):
        if not filename.endswith(".md"):
            continue
        with open(os.path.join(directory, filename)) as f:
            content = f.read()

        chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({"source": filename, "chunk": i})
            ids.append(f"{filename}_{i}")

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Loaded {len(documents)} chunks from {directory}")

load_documents("data/")
```

ChromaDB embeds the text automatically using a built-in model. No extra API key or GPU needed.

### 6.2. Create the search tool

```python
def search_knowledge_base(query: str) -> str:
    """Search the MLOps knowledge base for information about CI/CD, model monitoring, feature stores, and experiment tracking.

    Args:
        query: A natural language search query.

    Returns:
        The most relevant passages from the knowledge base.
    """
    results = collection.query(query_texts=[query], n_results=3)
    formatted = []
    for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
        formatted.append(f"[Source: {metadata['source']}]\n{doc}")
    return "\n\n---\n\n".join(formatted)
```

### 6.3. Build the RAG agent

```python
from agno.agent import Agent
from agno.models.google import Gemini

rag_agent = Agent(
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    tools=[search_knowledge_base],
    instructions="You are an MLOps expert. Use the knowledge base to answer questions. Always cite the source document.",
    markdown=True,
)

rag_agent.print_response(
    "What is training-serving skew and how do feature stores help prevent it?",
    stream=True,
)
```

Run it.

```bash
uv run python src/rag_agent.py
```

The agent searches ChromaDB, retrieves the most relevant chunks from your documents, and uses them to answer the question.

> **Note**: In production, you would use a managed service like Vertex AI Search to host your knowledge base. For this lab, ChromaDB running in-memory is enough.

## 7. Putting it all together

Create `src/agent.py` that combines everything into one multi-agent team with RAG.

```python
import os
import chromadb
from agno.agent import Agent
from agno.team import Team
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# --- RAG setup ---
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="mlops_knowledge")

def load_documents(directory):
    documents, metadatas, ids = [], [], []
    for filename in os.listdir(directory):
        if not filename.endswith(".md"):
            continue
        with open(os.path.join(directory, filename)) as f:
            content = f.read()
        chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({"source": filename, "chunk": i})
            ids.append(f"{filename}_{i}")
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Loaded {len(documents)} chunks")

load_documents("data/")

def search_knowledge_base(query: str) -> str:
    """Search the MLOps knowledge base for information about CI/CD, model monitoring, feature stores, and experiment tracking.

    Args:
        query: A natural language search query.

    Returns:
        The most relevant passages from the knowledge base.
    """
    results = collection.query(query_texts=[query], n_results=3)
    formatted = []
    for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
        formatted.append(f"[Source: {metadata['source']}]\n{doc}")
    return "\n\n---\n\n".join(formatted)

# --- Specialist agents ---
web_agent = Agent(
    name="Web Researcher",
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    tools=[DuckDuckGoTools()],
    instructions="You search the web for current information.",
)

finance_agent = Agent(
    name="Financial Analyst",
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    tools=[YFinanceTools(enable_stock_price=True, enable_analyst_recommendations=True, enable_company_news=True)],
    instructions="You analyze financial data. Always look up real numbers.",
)

mlops_agent = Agent(
    name="MLOps Expert",
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    tools=[search_knowledge_base],
    instructions="You answer questions about MLOps using the knowledge base. Always cite sources.",
)

# --- Team ---
team = Team(
    name="Expert Team",
    mode="coordinate",
    model=Gemini(id="gemini-2.5-flash", vertexai=True, project_id="YOUR_PROJECT_ID", location="europe-west1"),
    members=[web_agent, finance_agent, mlops_agent],
    instructions="You lead a team of experts. Route questions to the right specialist. For MLOps topics use the MLOps Expert. For finance use the Financial Analyst. For general research use the Web Researcher. Combine their answers into a clear final response.",
    markdown=True,
)

# --- Test ---
if __name__ == "__main__":
    team.print_response("What is model monitoring and why does it matter in production ML systems?", stream=True)
    print("\n" + "=" * 60 + "\n")
    team.print_response("How is NVIDIA stock doing and what is the latest AI chip news?", stream=True)
```

```bash
uv run python src/agent.py
```

## 8. Deploy as an API

### 8.1. Flask endpoint

Create `src/app.py`. Import the team from `agent.py` and expose it as an API.

```python
from flask import Flask, request, jsonify
from src.agent import team

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    response = team.run(question, stream=False)
    answer = response.content if hasattr(response, "content") else str(response)
    return jsonify({"answer": answer})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})
```

### 8.2. Dockerfile

```Dockerfile
FROM mirror.gcr.io/library/python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv export --frozen --no-dev --no-hashes -o /tmp/requirements.txt && \
    uv pip install --system -r /tmp/requirements.txt

COPY src/ ./src/
COPY data/ ./data/

ENV PORT=8080

CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "4", "--timeout", "120", "src.app:app"]
```

The `--timeout 120` is important. Agent loops make multiple LLM calls and can take 10-30 seconds. The default gunicorn timeout of 30 seconds would kill the request.

### 8.3. Build and test locally

```bash
docker build --platform linux/amd64 -t agent-api:latest .
docker run -p 8080:8080 \
  -v $HOME/.config/gcloud/application_default_credentials.json:/tmp/adc.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/adc.json \
  agent-api:latest
```

In another terminal, test the endpoint.

```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is model monitoring and why does it matter?"}'
```

### 8.4. Push and deploy

Create the Artifact Registry repository.

```bash
gcloud artifacts repositories create agent-repo \
    --repository-format=docker \
    --location=europe-west1 \
    --project=YOUR_PROJECT_ID
```

Tag and push.

```bash
gcloud auth configure-docker europe-west1-docker.pkg.dev
docker tag agent-api:latest \
    europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/agent-repo/agent-api:latest
docker push europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/agent-repo/agent-api:latest
```

Deploy to Cloud Run. On Cloud Run, the service automatically has access to Vertex AI through its service account. No API key or credentials file needed.

```bash
gcloud run deploy agent-api \
    --project=YOUR_PROJECT_ID \
    --image=europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/agent-repo/agent-api:latest \
    --region=europe-west1 \
    --port=8080 \
    --allow-unauthenticated
```

Test the deployed service.

```bash
curl -X POST https://YOUR_SERVICE_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the best practices for CI/CD in ML projects?"}'
```

## 9. Your turn

Build your own multi-agent system. The requirements are simple.

1. **At least 3 agents** working together in a team.
2. **At least one custom tool** you wrote yourself (not a built-in Agno tool).
3. **A knowledge base** with your own documents (not the ones provided in `data/`).
4. **Deployed on Cloud Run** and accessible via a POST endpoint.

Beyond that, get creative. Build a team of expert bots about topics you care about (finance, sports, cooking, gaming, science, etc.). Connect interesting tools.

Browse the [Agno built-in tools](https://docs.agno.com/tools/toolkits/overview) for inspiration. There are tools for Wikipedia, arXiv, HackerNews, Google Sheets, Slack, and many more.

### Deliverables

Submit the following on **Gradescope**.
- The URL of your deployed Cloud Run service
- A screenshot of the agent answering a question that required a tool call
- Your `src/` directory with all code

The service must be deployed and accessible on **Monday May 3rd at 23:59 AM**.

A pass grade requires the agent to be deployed on Cloud Run, respond to POST requests, use a multi-agent team with at least one custom tool, and include a knowledge base.

## 10. Cleanup

Delete the Cloud Run service.

```bash
gcloud run services delete agent-api --project=YOUR_PROJECT_ID --region=europe-west1
```

Delete the Artifact Registry repository.

```bash
gcloud artifacts repositories delete agent-repo \
    --location=europe-west1 \
    --project=YOUR_PROJECT_ID \
    --quiet
```
