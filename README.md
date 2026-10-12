# Department RAG Router

A Python multi-agent Retrieval-Augmented Generation (RAG) system for **AR Cloud**, a fictional company. Employee questions are routed to specialized Human Resources, Technology, or Finance agents, which generate answers grounded in departmental documents.

Built with LangChain, OpenAI, ChromaDB, Langfuse, and Pytest for an AI Engineering course project.

## Features

- LLM-based department routing with structured output.
- Three specialized agents and independent persistent ChromaDB collections.
- Token-aware document chunking, overlap, and source attribution.
- CLI with interactive and single-question modes.
- Langfuse traces for routing, retrieval, and generation.
- Routing, retrieval, and answer quality evaluation with a 1–10 LLM judge.
- Explicit out-of-scope detection and controlled fallback responses.
- LLM judge enabled by default during formal evaluations.
- Jupyter notebook and mocked unit tests.

## Architecture

```text
User question
     |
     v
LLM department router
     |
     +---- HR agent ---------- hr_documents
     +---- Technology agent -- technology_documents
     +---- Finance agent ----- finance_documents
     |
     +---- Out of scope ------ controlled fallback
     |
     v
Grounded answer or fallback response
     |
     +---- Langfuse traces
     +---- LLM judge (formal evaluation)
```

The router selects one of three specialized departments or classifies the question as out_of_scope. Department questions are answered using retrieved documents, while out-of-scope questions receive a controlled response without document retrieval.

## Technology Stack

| Technology | Role |
|---|---|
| Python 3.12 | Application language |
| LangChain / LangChain OpenAI | Model integration, structured output, document processing |
| OpenAI | Chat models, judge, and embeddings |
| ChromaDB / LangChain Chroma | Persistent vector retrieval |
| Tiktoken | Token-aware chunking |
| Langfuse | Traces and evaluation scores |
| Pytest | Automated unit tests |
| Jupyter / IPython Kernel | Interactive demonstration |
| Python Dotenv | Local configuration |

Versions are pinned in `requirements.txt`.

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
│   │   ├── department_agent.py
│   │   ├── hr_agent.py
│   │   ├── tech_agent.py
│   │   └── finance_agent.py
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
├── tests/
│   ├── test_router.py
│   ├── test_department_agent.py
│   ├── test_orchestrator.py
│   ├── test_retrieval.py
│   └── test_evaluation.py
├── storage/                 # Generated locally, excluded from Git
├── multi_agent_system.ipynb
├── test_queries.json
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### Clone and set up Python

```bash
git clone https://github.com/crisar0790/department-rag-router.git
cd department-rag-router
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, create the environment with `py -3.12 -m venv .venv` and activate it with `.venv\Scripts\Activate.ps1`.

### Configure credentials

```bash
cp .env.example .env
```

On Windows, use `Copy-Item .env.example .env` or copy the file manually.

Set these values in `.env`:

```dotenv
OPENAI_API_KEY=your-openai-api-key
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com
```

Other settings are documented in `.env.example`. Never commit `.env` or real credentials.

## Document Collections and Indexing

| Department | Chroma collection | Recorded chunks |
|---|---|---:|
| Human Resources | `hr_documents` | 53 |
| Technology | `technology_documents` | 51 |
| Finance | `finance_documents` | 56 |
| **Total** | | **160** |

The counts above come from the recorded indexing run. They may change if documents or chunking settings change.

Initial settings:

```dotenv
CHROMA_PERSIST_DIRECTORY=storage/chroma
CHUNK_SIZE_TOKENS=350
CHUNK_OVERLAP_TOKENS=50
```

Build all collections:

```bash
python -m src.retrieval.indexing --department all
```

Or rebuild one department:

```bash
python -m src.retrieval.indexing --department hr
```

Rebuild indexes after modifying documents, embeddings, or chunking parameters. Indexing uses the OpenAI embeddings API and incurs costs. The generated `storage/` directory is intentionally not committed.

## Running the Application

Single question:

```bash
python -m src.cli --question "How do I request annual leave?"
```

Interactive mode:

```bash
python -m src.cli
```

The system returns a department-specific answer with source references. Valid OpenAI and Langfuse credentials are required.


## Evaluation

`test_queries.json` contains 15 questions:

- 12 standard departmental questions.
- 2 cross-department questions.
- 1 out-of-scope question.

The evaluation measures department routing, document retrieval,
and generated answer quality.

### Full Evaluation

Run the complete evaluation, including the LLM judge:

```bash
python -m src.evaluation --k 3 --output evaluation/report.json
```

The LLM judge is enabled by default.

### Routing and Retrieval Only

To skip LLM quality evaluation:

```bash
python -m src.evaluation --k 3 --no-judge --output evaluation/routing_only.json
```

Use a separate output file to avoid overwriting the complete report.

### Evaluation Metrics

- **Routing accuracy:** Proportion of questions routed to their expected department, including `out_of_scope`.
- **Retrieval hit rate:** Proportion of applicable questions retrieving at least one expected document ID.
- **Average answer quality:** Mean LLM judge score from 1 to 10, considering faithfulness, completeness, and relevance.

Out-of-scope questions are included in routing accuracy but excluded
from retrieval and answer quality scoring.

Retrieval hit rate is a document-level metric. It does not measure
chunk-level precision or recall.

### Recorded Results

The committed `evaluation/report.json` contains:

| Metric | Result |
|---|---:|
| Total questions | 15 |
| Routing evaluated | 15 |
| Routing accuracy | 100% (15/15) |
| Retrieval evaluated | 14 |
| Retrieval hit rate | 100% (14/14) |
| Answers judged | 14 |
| Average answer quality | 9.93/10 |

These results apply to the supplied evaluation dataset and do not guarantee equivalent performance on unseen questions.

The LLM judge is a complementary quality signal rather than a substitute for independent human evaluation.

The recorded results represent a single evaluation run on a small, predefined dataset. Although all routing and retrieval cases passed, additional unseen, multilingual, and adversarial queries would be needed to assess robustness and generalization.

## Automated Testing

The project contains five Pytest modules:

| Test file | Main responsibility |
|---|---|
| `tests/test_router.py` | Input validation, routing decisions, callbacks |
| `tests/test_department_agent.py` | Context formatting, answers, sources |
| `tests/test_orchestrator.py` | Agent coordination, traces, error handling |
| `tests/test_retrieval.py` | Vector stores, retrieval, tracing |
| `tests/test_evaluation.py` | Metrics, judge, Langfuse scores |

Run all tests:

```bash
python -m pytest -v
```

Run an individual module:

```bash
python -m pytest tests/test_router.py -v
python -m pytest tests/test_evaluation.py -v
```

The tests mock external OpenAI, ChromaDB, and Langfuse interactions where appropriate, making unit tests fast and avoiding live API calls. They verify code behavior, while the evaluation pipeline tests the actual RAG workflow. Do not interpret passing mocked tests as proof of live model quality.

## Langfuse Observability

The root observation is named `department-rag-query`. The workflow records routing, retrieval, generation, and relevant metadata. When the judge is enabled, an `answer_quality` numeric score is submitted through the Langfuse Score API.

Open the configured Langfuse project, inspect **Tracing** for a `department-rag-query` trace, and review **Scores** for evaluation results. Provider telemetry may also expose latency, token usage, and estimated cost.

## Jupyter Notebook

`multi_agent_system.ipynb` demonstrates:

1. Setup and imports.
2. Document collections and vector stores.
3. Specialized department agents.
4. Router and orchestrator.
5. Tests and examples.
6. Langfuse observability.

Install dependencies, configure `.env`, build the indexes, open the notebook in VS Code or Jupyter, select the project's `.venv` kernel, and execute cells in order. Run from the repository root. The committed notebook includes saved execution outputs demonstrating retrieval, specialized agents, orchestration, out-of-scope handling, and evaluation results. Re-running the notebook requires valid credentials and locally generated vector indexes.

## Design Decisions and Trade-offs

These explanations distinguish **design rationale** from **measured evidence**. Unless stated otherwise, the configuration was not experimentally optimized through controlled comparisons.

### Department router and specialized agents

**Decision:** use an LLM router and three department-specific RAG agents rather than searching a single shared knowledge base.

**Why:** restricting retrieval to the chosen department reduces cross-domain context mixing and makes responsibilities explicit.

**Trade-off:** Incorrect routing prevents retrieval from the appropriate collection. Cross-department questions are assigned to a single department, potentially omitting relevant information from other departments. Out-of-scope detection depends on the accuracy of the LLM router and may produce false positives or false negatives.

**Evidence:** routing accuracy was 15/15 on the applicable evaluation cases. This is not a generalization guarantee.

### LangChain instead of custom orchestration

**Decision:** use LangChain for structured model outputs, model integration, document objects, and splitting.

**Why:** shared abstractions reduce boilerplate and keep components modular.

**Trade-off:** the project depends on library interfaces and version compatibility; dependencies are pinned. The workflow is sequential Python orchestration and does not require a LangGraph state machine.

### Persistent ChromaDB and independent collections

**Decision:** use locally persistent ChromaDB with separate collections for HR, Technology, and Finance.

**Why:** departmental isolation simplifies retrieval boundaries, and persistence avoids re-embedding documents on each execution.

**Trade-off:** local indexes require rebuilding on another machine; this setup is not designed for distributed production deployment or centralized access control.

### Chunk size: 350 tokens, overlap: 50 tokens

**Decision:** use token-aware recursive splitting with 350-token chunks and 50-token overlap.

**Why:** relatively compact chunks keep retrieval focused, while overlap helps preserve information crossing chunk boundaries.

**Trade-off:** smaller chunks can lose context, larger chunks can add irrelevant text, and overlap increases indexing/storage work.

**Evidence:** this configuration produced 160 indexed chunks across three departments. No alternative chunk-size or overlap settings were benchmarked.

### Embeddings: `text-embedding-3-small`

**Decision:** use `text-embedding-3-small` for document and query embeddings.

**Why:** it is a practical, relatively economical starting point for a small educational corpus.

**Trade-off:** retrieval quality may differ with other models, especially on ambiguous terminology. No comparative embedding benchmark was run. Switching models requires reindexing.

### Retrieval depth: `k=3`

**Decision:** retrieve three similar chunks by default.

**Why:** this limits the context sent to the answer model while allowing multiple supporting passages.

**Trade-off:** smaller `k` may miss evidence; larger `k` may introduce noise, latency, and cost.

**Evidence:** the recorded retrieval hit rate was 14/14 on applicable cases. There was no controlled comparison against other `k` values.

### Chat and evaluator: `gpt-5.5-2026-04-23`

**Decision:** configure this model for generation and LLM judging enabled by default during formal evaluation.

**Why:** a reasoning-capable model is a reasonable starting point for structured routing, grounded answering, and assessment.

**Trade-off:** access, latency, and price depend on API availability. A judge from the same model family is not guaranteed to be independent or unbiased.

**Evidence:** the recorded judge average was 9.93/10 on 14 answers. No controlled model or cost-quality comparison was conducted.

### Model request parameters

| Setting | Initial value | Rationale / limitation |
|---|---|---|
| `OPENAI_REASONING_EFFORT` | `low` | Limits initial reasoning effort; not compared experimentally with other levels. |
| `OPENAI_TIMEOUT` | `60` seconds | Allows time for reasoning-enabled calls; not tuned from measured latency distributions. |
| `OPENAI_MAX_RETRIES` | `0` | Exposes failures without hidden repeated requests; transient errors are not retried automatically. |
| `MAX_OUTPUT_TOKENS` | `2048` | Bounds generation output; not systematically tested against shorter limits. |

These are **initial, configurable settings**, not proven optimal values.

### Langfuse observability

**Decision:** trace routing, retrieval, and answer generation using Langfuse, and record LLM judge scores for formal evaluations by default. Quality scoring remains optional for regular user queries.

**Why:** traces support debugging, auditing retrieval decisions, and investigating answer quality.

**Trade-off:** tracing requires an external service and care with sensitive information in production.

### Evaluation design and LLM judge

**Decision:** combine deterministic routing/retrieval metrics with a structured 1–10 LLM judge.

**Why:** correct routing and a retrieval hit do not guarantee a complete or faithful answer; the judge adds a complementary quality signal.

**Trade-off:** judge scores can vary and may be biased. The 15-question dataset is small; human review and more varied cases would strengthen the evidence.

### Mocked unit tests versus functional evaluation

**Decision:** test internal control flow using mocks and assess real end-to-end behavior separately.

**Why:** mocked tests are reproducible and inexpensive, while live evaluation captures retrieval and generation quality.

**Trade-off:** passing unit tests cannot establish the reliability of external services or real model responses.

## Configuration and Reproducibility

Configuration is centralized in `src/config.py` and `.env.example`. Documented defaults:

```dotenv
OPENAI_CHAT_MODEL=gpt-5.5-2026-04-23
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EVALUATOR_MODEL=gpt-5.5-2026-04-23
OPENAI_REASONING_EFFORT=low
OPENAI_TIMEOUT=60
OPENAI_MAX_RETRIES=0
MAX_OUTPUT_TOKENS=2048
CHUNK_SIZE_TOKENS=350
CHUNK_OVERLAP_TOKENS=50
CHROMA_PERSIST_DIRECTORY=storage/chroma
```

Model access depends on the OpenAI account. To reproduce a run, install pinned dependencies, configure credentials, rebuild the vector indexes, and rerun the evaluation. Outputs may vary across model executions.

## Known Limitations

- The system supports three predefined departments.
- Cross-department questions are routed to a single department.
- Out-of-scope detection depends on LLM classification accuracy.
- The fictional knowledge base and evaluation dataset are limited.
- Document-level retrieval hit rate does not measure chunk-level
  precision or recall.
- LLM judge scores may vary and may exhibit model-related bias.
- The evaluator uses the same model family as the application,
  limiting judge independence.
- No controlled comparison of models, embeddings, chunk sizes,
  overlaps, or retrieval depth has been conducted.
- Local vector indexes must be regenerated after relevant changes.
- Live API requests incur costs and require valid credentials.

## Potential Improvements

- Support multi-department retrieval for cross-domain questions.
- Benchmark models, embeddings, chunk sizes, overlaps, and `k`.
- Add retrieval precision/recall and human-reviewed evaluation cases.
- Track latency, tokens, and API cost alongside quality.
- Expand regression coverage and introduce CI.
- Add production privacy safeguards and access controls.

## License

Developed for educational purposes as part of an AI Engineering course. No separate open-source license has been specified.
