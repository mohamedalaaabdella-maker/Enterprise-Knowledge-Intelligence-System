# Enterprise Knowledge Intelligence System

Advanced RAG system over technical documentation.

## Pipeline

Documents → Processing → Chunking → Embeddings → Chroma → Dense Retrieval + BM25 → Hybrid Search → Reranking → Grounded Generation → Evaluation → Streamlit

## Project Structure

```text
enterprise-rag/
├── data/
│   ├── documents/
│   └── evaluation/
├── src/
│   ├── ingestion/
│   │   ├── loaders.py
│   │   ├── cleaner.py
│   │   └── chunker.py
│   ├── retrieval/
│   │   ├── dense.py
│   │   ├── bm25.py
│   │   ├── hybrid.py
│   │   └── reranker.py
│   ├── generation/
│   │   ├── prompts.py
│   │   └── llm.py
│   ├── evaluation/
│   │   └── metrics.py
│   ├── pipeline.py
│   └── config.py
├── app/
│   └── streamlit_app.py
├── notebooks/
├── vectorstore/
├── tests/
├── .env.example
├── .gitignore
└── requirements.txt
```

## Getting Started

1. Create a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and fill in the required LLM settings.
4. Place the prepared dataset inside `data/documents/` and `data/evaluation/`.
5. Implement the phases sequentially; do not skip evaluation.
