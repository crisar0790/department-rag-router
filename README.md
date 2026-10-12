
# Department RAG Router

A Python multi-agent Retrieval-Augmented Generation (RAG) system that routes employee questions to specialized Human Resources, Technology, and Finance agents.

The project uses LangChain, OpenAI, ChromaDB, and Langfuse to provide grounded answers, persistent document retrieval, execution tracing, and automated evaluation.

## Features

- LLM-based intent classification and department routing.
- Three specialized RAG agents with independent knowledge collections.
- Persistent ChromaDB vector stores.
- Document chunking with token-based overlap.
- Source attribution for generated answers.
- Interactive and one-shot command-line interfaces.
- Langfuse tracing for routing, retrieval, and generation.
- Automated routing and retrieval evaluation.
- Optional LLM judge with scores from 0 to 10.
- Langfuse Score API integration.
- Jupyter notebook demonstrating the complete workflow.

## Architecture

```text
User Question
      |
      v
  LLM Router
      |
      +---- HR Agent -------- HR Chroma Collection
      |
      +---- Technology Agent - Technology Chroma Collection
      |
      +---- Finance Agent ---- Finance Chroma Collection
      |
      v
Grounded Answer + Sources
      |
      +---- Langfuse Tracing
      |
      +---- Optional LLM Judge
                    |
                    v
              Langfuse Scores
```

The router classifies the question into a department. The corresponding agent retrieves relevant document chunks and uses them to generate a grounded response.

Langfuse records execution details, while the evaluation pipeline measures routing accuracy, retrieval performance, and answer quality.

## Technology Stack

- Python 3.12
- LangChain and LangChain OpenAI
- OpenAI chat and embedding models
- ChromaDB and LangChain Chroma
- Langfuse
- Tiktoken
- Jupyter and IPython Kernel
- Pytest
- Python Dotenv

Exact dependency versions are defined in `requirements.txt`.

## Project Structure

```text
department-rag-router/
├── data/
│   ├── hr_docs/
│   ├── tech_docs/
│   └── finance_docs/
├── evaluation/
│   └── report.json
├── src/
│   ├── agents/
│   │   └── department_agent.py
│   ├── retrieval/
│   │   ├── chunking.py
│   │   ├── indexing.py
│   │   └── retriever.py
│   ├── cli.py
│   ├── config.py
│   ├── evaluation.py
│   ├── evaluator.py
│   ├── models.py
│   ├── observability.py
│   ├── orchestrator.py
│   └── router.py
├── storage/
├── multi_agent_system.ipynb
├── test_queries.json
├── requirements.txt
├── .env.example
└── README.md
```

The `storage/` directory contains the locally generated vector database and is not required to be committed. It can be recreated using the indexing command.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/crisar0790/department-rag-router.git
cd department-rag-router
```

### 2. Create a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the environment template:

```bash
cp .env.example .env
```

On Windows, create a copy of `.env.example` named `.env`.

Configure the required credentials:

```dotenv
OPENAI_API_KEY=your-openai-api-key

LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com
```

The environment template also defines:

- `OPENAI_CHAT_MODEL`
- `OPENAI_EMBEDDING_MODEL`
- `OPENAI_EVALUATOR_MODEL`
- `OPENAI_REASONING_EFFORT`
- `OPENAI_TIMEOUT`
- `OPENAI_MAX_RETRIES`
- `MAX_OUTPUT_TOKENS`
- `CHROMA_PERSIST_DIRECTORY`
- `CHUNK_SIZE_TOKENS`
- `CHUNK_OVERLAP_TOKENS`

Never commit the `.env` file or actual API credentials.

## Document Collections

The project contains three departmental knowledge bases:

| Department | Collection | Indexed chunks |
|---|---|---:|
| Human Resources | `hr_documents` | 53 |
| Technology | `technology_documents` | 51 |
| Finance | `finance_documents` | 56 |
| **Total** | | **160** |

Documents are split into overlapping chunks using token-aware splitting.

The configured initial chunking parameters are:

```dotenv
CHUNK_SIZE_TOKENS=350
CHUNK_OVERLAP_TOKENS=50
```

These values control chunk size and overlap and can be adjusted through the environment configuration.

### Build the vector stores

Run:

```bash
python -m src.retrieval.indexing --department all
```

This creates the persistent ChromaDB collections using OpenAI embeddings.

The indexing process requires an OpenAI API key and incurs embedding API costs.

Reindex after modifying source documents or changing chunking parameters.

## Running the Application

### One-shot mode

```bash
python -m src.cli --question "How do I request annual leave?"
```

### Interactive mode

```bash
python -m src.cli
```

The system routes each question to the relevant department and returns an answer with supporting document sources.

## Evaluation

The evaluation dataset is stored in `test_queries.json`.

It contains 15 test questions covering:

- Human Resources
- Technology
- Finance
- Edge cases, including an out-of-scope question

### Evaluate routing and retrieval

```bash
python -m src.evaluation
```

### Evaluate with the LLM judge

```bash
python -m src.evaluation --judge
```

The evaluation report is saved to:

```text
evaluation/report.json
```

The evaluation calculates:

**Routing accuracy:** the proportion of applicable questions routed to the expected department.

**Retrieval hit rate:** the proportion of applicable questions for which at least one expected document ID was retrieved.

**Average answer quality:** the mean LLM judge score, from 0 to 10, across evaluated answers.

The LLM judge evaluates faithfulness, completeness, and relevance using the retrieved context.

Out-of-scope cases without expected documents or departments are excluded from the corresponding metrics.

### Recorded Evaluation Results

The following results were obtained from the completed 15-query evaluation:

| Metric | Result |
|---|---:|
| Total queries | 15 |
| Routing accuracy | 100% (14/14) |
| Retrieval hit rate | 100% (14/14) |
| Evaluated answer quality cases | 14 |
| Average answer quality | 9.71/10 |

These results describe the supplied evaluation dataset. They do not guarantee equivalent performance on unseen questions.

The retrieval hit rate measures whether at least one expected document was retrieved; it is not a measure of precision for every retrieved chunk.

## Langfuse Observability

Langfuse records the execution of the RAG workflow.

The main trace is named:

```text
department-rag-query
```

The trace includes the routing workflow, retrieval operations, model generations, and associated execution information.

Depending on the available provider data, Langfuse can display latency, token usage, and estimated model costs.

The optional evaluator records an `answer_quality` score using the Langfuse Score API.

To inspect execution details:

1. Open the configured Langfuse project.
2. Navigate to **Tracing**.
3. Open a `department-rag-query` trace.
4. Inspect its nested observations.
5. Navigate to **Scores** to inspect evaluation results.

Langfuse credentials must be configured before running the traced workflow.

## Jupyter Notebook

The demonstration notebook is:

```text
multi_agent_system.ipynb
```

It contains six sections:

1. Setup and Imports
2. Document Collections and Vector Stores
3. Specialized Department Agents
4. Router and Orchestrator
5. Tests and Examples
6. Langfuse Observability

### Execution instructions

1. Install dependencies.
2. Configure `.env`.
3. Build the vector stores.
4. Open the notebook in VS Code or Jupyter.
5. Select the project's `.venv` Python kernel.
6. Execute the cells in order using **Run All**.

The notebook demonstrates document retrieval, agent execution, department routing, grounded answers, evaluation results, and observability.

Run the notebook from the repository root so that project imports and relative paths resolve correctly.

## Testing

Pytest is included as a development dependency.

Run any available automated tests with:

```bash
python -m pytest
```

The evaluation pipeline provides an additional functional validation of routing, retrieval, and answer generation.

## Configuration and Reproducibility

The project uses environment variables to configure model selection, request limits, document chunking, and vector database storage.

The default environment template specifies:

- Chat model: `gpt-5.5-2026-04-23`
- Evaluator model: `gpt-5.5-2026-04-23`
- Embedding model: `text-embedding-3-small`
- Reasoning effort: `low`
- Request timeout: 60 seconds
- Maximum retries: 0
- Maximum output tokens: 2048

These are configuration choices rather than experimentally proven optimal values.

Model access and availability depend on the OpenAI account and API configuration.

## Known Limitations

- Routing supports three predefined departments.
- The document collections contain a limited fictional organizational knowledge base.
- Out-of-domain questions are not handled by a dedicated rejection route.
- Retrieval evaluation uses document-level hits rather than chunk-level precision.
- The LLM judge is an automated evaluator and may exhibit scoring variability.
- Changes to embedding models or chunking parameters may require rebuilding the vector stores.
- API usage for indexing, answering, and evaluation incurs costs.
- The application requires valid OpenAI and Langfuse credentials.

## Potential Improvements

- Introduce a dedicated out-of-scope routing decision.
- Add retrieval precision and recall metrics.
- Evaluate alternative models and chunking configurations.
- Expand the evaluation dataset.
- Introduce confidence thresholds and fallback behavior.
- Add automated regression tests and CI workflows.
- Compare answer quality across different retrieval settings.

## License

This project was developed for educational purposes as part of an AI Engineering course.
