# Evaluation Dataset — Enterprise Knowledge Intelligence System

## 1. Purpose

This dataset evaluates an Advanced RAG system built over a small, curated
corpus of technical documentation spanning Python, FastAPI, Docker,
PostgreSQL and Git (`../documents/`). It is designed to stress different
retrieval strategies — dense (embedding) retrieval, BM25 (keyword) retrieval,
hybrid retrieval, and hybrid + cross-encoder reranking — as well as the
generation stage that produces grounded, cited answers from retrieved
context.

## 2. Number of Questions

**71 questions** across the five domains and eight categories described
below.

## 3. Question Categories

| Category | Count | What it tests |
| :--- | :--- | :--- |
| `direct` | 13 | Answer stated clearly in one document, in similar wording to the question. |
| `semantic` | 11 | Paraphrased questions that avoid the source's exact terminology, to test embedding-based retrieval rather than lexical overlap. |
| `keyword` | 13 | Questions built around exact technical terms, flags, error codes, or identifiers (e.g. `git reset --hard`, `23505`, `EXPOSE`), to test BM25 / lexical retrieval. |
| `disambiguation` | 11 | Pairs of closely related concepts that must be told apart (e.g. `git reset` vs `git revert`, image vs container, path vs query parameter), important for reranking. |
| `multi_document` | 4 | Answers that require combining information from two documents, usually across domains (e.g. FastAPI + Docker, PostgreSQL + Docker). |
| `multi_hop` | 5 | Answers that require chaining two or more facts together (e.g. container ephemerality → volumes → data persistence). |
| `difficult` | 6 | Cases where several documents could look relevant, or where the "right" answer depends on picking the correct one of several similar mechanisms (e.g. reset vs restore vs revert; LEFT JOIN vs INNER JOIN). |
| `out_of_scope` | 8 | Questions about technologies or facts not in the corpus (MongoDB, Kubernetes, React, general knowledge). These should trigger an "I don't have enough information" response rather than a hallucinated answer. |

Domain distribution (by the `domain` field, including multi-document
combinations such as `fastapi_docker`):

| Domain | Count |
| :--- | :--- |
| git | 14 |
| python | 13 |
| docker | 13 |
| postgresql | 10 |
| fastapi | 9 |
| unknown (out-of-scope) | 8 |
| fastapi_docker | 2 |
| postgresql_docker | 1 |
| git_docker | 1 |

All five documentation domains are represented in both single-domain and
multi-document questions, and all eight categories appear for at least
one domain.

## 4. JSON Schema

`questions.json` is a JSON array. Each entry has:

```json
{
  "question_id": "q001",
  "question": "...",
  "category": "direct | semantic | keyword | disambiguation | multi_document | multi_hop | difficult | out_of_scope",
  "domain": "python | fastapi | docker | postgresql | git | <domain>_<domain> | unknown",
  "ground_truth": "... (string, or null for out_of_scope questions)",
  "relevant_documents": ["document_id", "..."]
}
```

`domain` uses an underscore-joined combination (e.g. `fastapi_docker`) for
`multi_document` questions that span two domains, and `unknown` for
`out_of_scope` questions, matching the convention in the task
specification.

## 5. Meaning of `relevant_documents`

`relevant_documents` lists the `document_id`s (matching
`../documents/metadata.json`) whose content is **genuinely required** to
answer the question — not merely topically related. For direct, semantic
and keyword questions this is normally a single document. For
disambiguation questions it is usually the (up to) two documents that
describe each side of the distinction. For multi-document and multi-hop
questions it is every document contributing a necessary fact. For
`out_of_scope` questions it is always an empty list, since no document in
the corpus should be treated as relevant.

Every `ground_truth` was checked by locating each factual claim as a
(possibly paraphrased) passage inside the listed `relevant_documents`;
nothing was written from general knowledge that isn't present in the
corpus.

## 6. Use for Retrieval Evaluation

For each non-out-of-scope question, treat `relevant_documents` as the
relevance set and the retriever's top-K results as the ranked list
returned for the question. This supports the standard retrieval metrics:

- **Precision@K** — fraction of the top-K retrieved documents that are in `relevant_documents`.
- **Recall@K** — fraction of `relevant_documents` found in the top-K.
- **Hit Rate@K** — whether at least one relevant document appears in the top-K.
- **MRR** — reciprocal rank of the first relevant document retrieved.
- **MAP** — mean of per-question average precision over all relevant documents.
- **nDCG** — rank-discounted gain, treating any document in `relevant_documents` as equally relevant (graded relevance was not assigned).

`out_of_scope` questions are excluded from these document-relevance
metrics (their relevance set is empty by design) but should be used
separately to check that the retriever does not return highly-scored
documents with unwarranted confidence, and that the generator recognizes
the absence of support and declines to answer rather than hallucinating.

Compare retrieval methods (dense vs BM25 vs hybrid vs hybrid+reranking) by
computing these metrics per category — `keyword` questions are expected to
favor BM25/hybrid, `semantic` questions are expected to favor dense
retrieval, and `disambiguation`/`difficult` questions are the ones
reranking is expected to help most.

## 7. Use for Generation Evaluation

Once an answer is generated from the retrieved context, compare it against
`ground_truth` (for non-out-of-scope questions) to assess:

- **Faithfulness** — does the generated answer only state things supported by the retrieved context (no unsupported claims)?
- **Answer Relevance** — does the generated answer actually address the question asked?
- **Context Relevance** — how much of the retrieved context was actually needed to produce the ground-truth answer (penalizes retrieving irrelevant chunks)?
- **Correctness** — does the generated answer match the factual content of `ground_truth`, allowing for different wording?

For `out_of_scope` questions, generation evaluation checks that the system
explicitly states it lacks sufficient information in the knowledge base,
rather than fabricating an answer from the model's own general knowledge.
