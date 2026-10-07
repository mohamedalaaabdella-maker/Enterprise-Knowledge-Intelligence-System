# Enterprise Knowledge Intelligence System

An advanced **Retrieval-Augmented Generation (RAG)** system for answering technical questions from enterprise documentation.

The system combines **Dense Retrieval, BM25, Hybrid Retrieval with Reciprocal Rank Fusion (RRF), Cross-Encoder Reranking, Query Rewriting, Relevance Checking, and LLM-based Generation** to provide grounded answers from technical documentation.

The knowledge base currently covers:

* Python
* FastAPI
* Docker
* PostgreSQL
* Git

---

## Overview

Traditional LLM applications can generate plausible answers even when the underlying information is missing from the model's knowledge.

This project addresses that problem by grounding generated answers in a controlled technical documentation knowledge base.

Instead of directly asking an LLM:

```text
User Question
      ↓
     LLM
      ↓
   Answer
```

the system uses a multi-stage RAG pipeline:

```text
User Question
      │
      ▼
Dense Retrieval ─────────┐
                         │
BM25 Retrieval ──────────┤
                         ▼
                Reciprocal Rank Fusion
                         │
                         ▼
                  Candidate Documents
                         │
                         ▼
                    Reranking
                         │
                         ▼
                    Top-5 Context
                         │
                         ▼
                  Relevance Check
                    │         │
                  Good        Bad
                    │          │
                    │      Query Rewrite
                    │          │
                    │      Retrieval Again
                    │          │
                    └────┬─────┘
                         ▼
                     Generation
                         │
                         ▼
                    Final Answer
```

---

# Key Features

### Hybrid Retrieval

Combines two complementary retrieval strategies:

**Dense Retrieval**

Uses semantic embeddings to retrieve documents based on meaning.

**BM25**

Uses lexical matching to retrieve documents based on important terms and keywords.

The two retrieval results are combined using **Reciprocal Rank Fusion (RRF)**.

---

### Cross-Encoder Reranking

The retrieved candidates are reranked using:

```text
BAAI/bge-reranker-base
```

The reranker evaluates the relationship between the:

```text
Query + Document
```

and selects the most relevant documents.

The current system uses:

```text
Top-20 retrieval candidates
        ↓
Reranking
        ↓
Top-5 documents
```

---

### Query Rewriting

When the retrieved context is not considered sufficiently relevant, the system can rewrite the original query and perform retrieval again.

Example:

```text
Original Query
      ↓
Relevance Check
      ↓
Not Relevant
      ↓
Query Rewriting
      ↓
Retrieval Again
      ↓
Reranking
      ↓
Generation
```

This provides a corrective retrieval path for difficult queries.

---

### Relevance Checking

Before generation, an LLM-based relevance checker determines whether the retrieved context contains enough useful information to answer the original question.

If the context is insufficient, the system can trigger query rewriting.

---

### Grounded Generation

The generation prompt instructs the LLM to:

* Use only the retrieved context.
* Avoid unsupported information.
* Avoid hallucinating facts.
* Clearly indicate when the available context is insufficient.

---

### Source Transparency

The application exposes the retrieved documents and their metadata, allowing users to inspect the evidence used by the RAG system.

---

# Technology Stack

| Component            | Technology                   |
| -------------------- | ---------------------------- |
| Programming Language | Python                       |
| RAG Framework        | LangChain                    |
| Embeddings           | BAAI/bge-base-en-v1.5        |
| Vector Database      | Chroma                       |
| Dense Retrieval      | Semantic Vector Search       |
| Lexical Retrieval    | BM25                         |
| Hybrid Retrieval     | Reciprocal Rank Fusion       |
| Reranking            | BAAI/bge-reranker-base       |
| LLM Interface        | OpenAI-compatible API        |
| Structured Output    | Pydantic                     |
| UI                   | Gradio                       |
| Evaluation           | LLM-as-a-Judge               |
| Environment          | Python / CUDA-compatible GPU |

---

# Project Architecture

```text
Enterprise-Knowledge-Intelligence-System/
│
├── app/
│   └── gradio_app.py
│
├── data/
│   ├── documents/
│   │   ├── python/
│   │   ├── fastapi/
│   │   ├── docker/
│   │   ├── postgresql/
│   │   └── git/
│   │
│   ├── evaluation/
│   │   └── questions.json
│   │
│   └── metadata.json
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_chunking.ipynb
│   ├── 03_retrieval_experiments.ipynb
│   └── 04_evaluation.ipynb
│
├── src/
│   │
│   ├── ingestion/
│   │   ├── loaders.py
│   │   ├── cleaner.py
│   │   └── chunker.py
│   │
│   ├── retrieval/
│   │   ├── dense.py
│   │   ├── bm25.py
│   │   ├── hybrid.py
│   │   └── reranker.py
│   │
│   ├── generation/
│   │   ├── llm.py
│   │   ├── prompt.py
│   │   ├── relevance.py
│   │   └── generator.py
│   │
│   ├── evaluation/
│   │   └── metrics.py
│   │
│   ├── config.py
│   └── pipeline.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Data Ingestion

The system loads technical Markdown documentation together with document-level metadata.

Each document contains metadata such as:

```text
document_id
domain
file_path
```

The ingestion pipeline converts the raw files into LangChain `Document` objects.

---

# Cleaning

The cleaning stage performs lightweight normalization while preserving the original technical structure.

The system avoids aggressive preprocessing because Markdown structure, headings, code, commands, and technical terminology are important for retrieval.

---

# Structure-Aware Chunking

Documents are first split according to their Markdown hierarchy:

```text
#
##
###
####
```

Large sections are then further divided using a recursive character splitter.

Current configuration:

```text
Chunk Size: 1000 characters
Chunk Overlap: 150 characters
```

Each chunk receives a stable identifier:

```text
document_id_000
document_id_001
document_id_002
...
```

This allows the different retrieval stages to reference the same chunk consistently.

---

# Retrieval Pipeline

## 1. Dense Retrieval

The embedding model:

```text
BAAI/bge-base-en-v1.5
```

converts documents and queries into vector representations.

The system performs semantic similarity search using Chroma.

---

## 2. BM25 Retrieval

BM25 provides lexical retrieval and is particularly useful when the query contains:

* technical terminology
* function names
* configuration names
* commands
* exact keywords

---

## 3. Reciprocal Rank Fusion

The dense and BM25 rankings are combined using RRF.

The score contribution of a document at rank `r` is:

```text
1 / (k + r)
```

with:

```text
k = 60
```

Documents appearing in both retrieval rankings receive additional support.

---

# Reranking

After hybrid retrieval, the candidate documents are passed to a Cross-Encoder reranker.

```text
Hybrid Retrieval
       ↓
Top 20 Candidates
       ↓
BGE Reranker
       ↓
Top 5 Documents
```

The final five documents provide the context used by the generation stage.

---

# Query Rewriting

The system contains a corrective retrieval mechanism.

If the relevance checker determines that the retrieved context is insufficient:

```text
Question
   ↓
Retrieval
   ↓
Reranking
   ↓
Relevance Check
   ↓
Not Relevant
   ↓
Query Rewrite
   ↓
Retrieval Again
```

The rewritten query is used only for the retrieval process while the original user question remains the question being answered.

---

# Generation

The final answer is generated using the reranked context.

The generation prompt follows a grounded-answering strategy:

```text
Use only the provided context.
Do not use outside knowledge.
Do not invent information.
If the context is insufficient, say so.
```

This helps reduce unsupported generation and keeps the answer connected to the retrieved documentation.

---

# Evaluation

The system was evaluated at both the **retrieval** and **generation** levels.

## Retrieval Evaluation

The evaluation dataset contains:

```text
71 total questions
63 in-scope questions
8 out-of-scope questions
```

The retrieval evaluation measures:

* Precision@K
* Recall@K
* Hit Rate@K
* Mean Reciprocal Rank (MRR)

### In-Scope Retrieval Results

| Metric    | Top-5 | Top-8 | Top-10 |
| --------- | ----: | ----: | -----: |
| Precision | 63.4% | 48.0% |  36.0% |
| Recall    | 91.8% | 93.4% |  94.2% |
| Hit Rate  | 96.8% | 98.4% |  98.4% |

Overall:

```text
MRR = 91.2%
```

The retrieval results indicate that relevant information is usually retrieved near the top of the ranking.

The system achieved:

```text
54 / 63
```

relevant results at Rank 1.

And:

```text
62 / 63
```

in-scope questions had a relevant document within the Top-10.

---

# Generation Evaluation

Generated answers are evaluated using an **LLM-as-a-Judge** approach.

Three metrics are used:

### Faithfulness

Measures whether the generated answer is supported by the retrieved context.

### Answer Relevance

Measures whether the answer directly addresses the user's question.

### Correctness

Measures whether the answer is factually correct compared with the ground-truth answer.

Each metric produces:

```text
Score: 0 → 1
Reason: Short explanation
```

Generation evaluation was performed on a subset of the in-scope evaluation questions.

The evaluation results showed generally strong generation quality, with most scores falling in the high range.

---

# Why Hybrid Retrieval?

Different retrieval methods solve different problems.

Dense retrieval is strong at:

```text
Semantic similarity
Paraphrased questions
Conceptual queries
```

BM25 is strong at:

```text
Exact terminology
Technical keywords
Commands
Function names
```

Combining both allows the system to benefit from both semantic and lexical retrieval.

---

# Why Reranking?

Initial retrieval focuses on finding a broad set of potentially relevant documents.

The reranker performs a more precise relevance assessment.

Therefore:

```text
Retriever
→ Candidate Recall

Reranker
→ Relevance Precision
```

This two-stage architecture provides a better balance between retrieval coverage and final context quality.

---

# Example Questions

The system can answer questions such as:

```text
What is dependency injection in FastAPI?
```

```text
How do Docker containers communicate with each other?
```

```text
What is the difference between a Docker image and a container?
```

```text
How can PostgreSQL be connected to a containerized application?
```

```text
How does Git determine the exact commit used during a Docker image build?
```

---

# Running the Project

## 1. Clone the Repository

```bash
git clone https://github.com/mohamedalaaabdella-maker/Enterprise-Knowledge-Intelligence-System.git

cd Enterprise-Knowledge-Intelligence-System
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file:

```env
LLM_API_KEY=your_api_key
LLM_MODEL=your_model
LLM_BASE_URL=https://api.groq.com/openai/v1
```

Do not commit `.env` to GitHub.

Use `.env.example` as a template.

---

## 5. Run the Gradio Application

```bash
python app/gradio_app.py
```

The application launches the Gradio interface and provides a local or shareable URL depending on the environment.

---

# GPU Support

The project uses Hugging Face models for embeddings and reranking.

The current configuration uses:

```python
device="cuda"
```

for model inference.

A CUDA-compatible environment is therefore recommended for faster execution.

The application can be adapted for CPU execution by changing the model device configuration, although inference will generally be slower.

---

# Evaluation Notebooks

The repository contains notebooks for exploring and evaluating different stages of the system:

```text
01_data_exploration.ipynb
```

Explores the documentation dataset and metadata.

```text
02_chunking.ipynb
```

Experiments with cleaning and structure-aware chunking.

```text
03_retrieval_experiments.ipynb
```

Evaluates dense, BM25, hybrid retrieval, RRF, and reranking.

```text
04_evaluation.ipynb
```

Evaluates the final retrieval and generation quality.

---

# Design Principles

The project follows several practical RAG design principles:

### Grounded Generation

The LLM should answer from retrieved evidence rather than relying on unsupported knowledge.

### Hybrid Retrieval

Semantic and lexical retrieval complement each other.

### Two-Stage Retrieval

Broad candidate retrieval is followed by precise reranking.

### Corrective Retrieval

Poor retrieval can trigger query rewriting and another retrieval attempt.

### Evaluation-Driven Development

Retrieval and generation are evaluated independently rather than judging the system only from example outputs.

### Traceability

Retrieved documents and metadata are preserved so the final answer can be connected to its evidence.

---

# Future Improvements

Potential future improvements include:

* Better multi-document retrieval strategies
* Document-level diversity during retrieval
* More advanced query rewriting
* Additional reranking experiments
* Improved answer citation and source attribution
* Expanded evaluation datasets
* More detailed observability and tracing
* Authentication and access control
* Production deployment
* Persistent retrieval indexes
* Evaluation dashboards

These are future directions and are not currently implemented unless explicitly described above.

---

# Project Status

The current implementation includes:

* [x] Document ingestion
* [x] Document cleaning
* [x] Structure-aware chunking
* [x] Dense retrieval
* [x] BM25 retrieval
* [x] Hybrid retrieval
* [x] Reciprocal Rank Fusion
* [x] Cross-Encoder reranking
* [x] Query rewriting
* [x] Relevance checking
* [x] Grounded answer generation
* [x] Retrieval evaluation
* [x] Generation evaluation
* [x] Gradio interface

---

# Author

**Mohamed Alaa Abdella**

AI Engineer focused on:

* Machine Learning
* Deep Learning
* Computer Vision
* NLP
* Generative AI
* Retrieval-Augmented Generation
* Agentic AI

GitHub:

`mohamed-alaa-abdella-maker`

---

## License

This project is intended for educational, portfolio, and research purposes.
