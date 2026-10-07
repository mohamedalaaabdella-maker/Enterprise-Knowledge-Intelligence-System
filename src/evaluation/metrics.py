from langchain_core.documents import Document
from pydantic import BaseModel , Field
from src.generation.llm import create_llm
import time
import random

class RetrievalMetrics:
    """
    Calculate retrieval metrics at the document level.

    Retrieved results are chunks, but evaluation is performed
    using the document_id stored in each chunk's metadata.
    """

    def __init__(
        self,
        retrieved_documents: list[Document],
        relevant_documents: list[str],
    ):
        self.retrieved_documents = retrieved_documents
        self.relevant_documents = relevant_documents

    # =========================================================
    # Document IDs
    # =========================================================

    def get_document_ids(
        self,
        documents: list[Document],
    ) -> list[str]:
        """
        Extract document_id from retrieved chunks.
        """

        return [
            document.metadata["document_id"]
            for document in documents
        ]    

    def get_unique_document_ids(
        self,
        documents: list[Document],
    ) -> list[str]:
        """
        Extract unique document_ids while preserving
        their original retrieval order.
        """

        document_ids = self.get_document_ids(
            documents
        )

        return list(dict.fromkeys(document_ids))

  
    # =========================================================
    # Precision@K
    # =========================================================

    def precision_at_k(
        self,
        k: int,
    ) -> float:
        """
        Calculate Precision@K at the document level.

        Precision@K =
        relevant retrieved documents / unique retrieved documents
        """

        retrieved_ids = self.get_unique_document_ids(
            self.retrieved_documents[:k]
        )

        relevant_ids = set(
            self.relevant_documents
        )

        if not retrieved_ids:
            return 0.0

        relevant_retrieved = sum(
            document_id in relevant_ids
            for document_id in retrieved_ids
        )

        return relevant_retrieved / len(
            retrieved_ids
        )

    # =========================================================
    # Recall@K
    # =========================================================

    def recall_at_k(
        self,
        k: int,
    ) -> float:
        """
        Calculate Recall@K at the document level.

        Recall@K =
        relevant retrieved documents / all relevant documents
        """

        retrieved_ids = set(
            self.get_document_ids(
                self.retrieved_documents[:k]
            )
        )

        relevant_ids = set(
            self.relevant_documents
        )

        if not relevant_ids:
            return 0.0

        relevant_retrieved = len(
            retrieved_ids & relevant_ids
        )

        return relevant_retrieved / len(
            relevant_ids
        )


    # =========================================================
    # Hit Rate@K
    # =========================================================

    def hit_rate_at_k(
        self,
        k: int,
    ) -> float:
        """
        Return 1.0 if at least one relevant document
        appears in the top-K retrieved chunks.
        Otherwise return 0.0.
        """

        retrieved_ids = set(
            self.get_document_ids(
                self.retrieved_documents[:k]
            )
        )

        relevant_ids = set(
            self.relevant_documents
        )

        return float(
            bool(retrieved_ids & relevant_ids)
        )


    # =========================================================
    # Reciprocal Rank
    # =========================================================

    def reciprocal_rank(self) -> float:
        """
        Calculate the Reciprocal Rank of the first
        relevant retrieved document.

        Reciprocal Rank = 1 / rank

        Returns 0.0 if no relevant document is retrieved.
        """

        relevant_ids = set(
            self.relevant_documents
        )

        for rank, document in enumerate(
            self.retrieved_documents,
            start=1,
        ):
            document_id = document.metadata["document_id"]

            if document_id in relevant_ids:
                return 1 / rank

        return 0.0

    # =========================================================
    # All Metrics
    # =========================================================

    def calculate(
        self,
        k: int,
    ) -> dict[str, float]:
        """
        Calculate all retrieval metrics for a given K.
        """

        return {
            f"precision@{k}": self.precision_at_k(k),
            f"recall@{k}": self.recall_at_k(k),
            f"hit_rate@{k}": self.hit_rate_at_k(k),
            "reciprocal_rank": self.reciprocal_rank(),
        }    


# =========================================================
# Evaluation Result
# =========================================================

class EvaluationResult(BaseModel):
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Evaluation score between 0 and 1."
    )

    reason: str = Field(
        description="Short explanation for the given score."
    )


# =========================================================
# Generation Evaluator
# =========================================================

class GenerationEvaluator:
    """
    Evaluate generated answers using LLM-as-a-Judge.

    Metrics:
    - Faithfulness
    - Answer Relevance
    - Correctness
    """

    def __init__(self):
        self.llm = create_llm()

        self.evaluator = self.llm.with_structured_output(
            EvaluationResult
        )


    # =====================================================
    # LLM Invocation with Retry
    # =====================================================

    def _invoke_with_retry(
        self,
        prompt: str,
        max_retries: int = 5,
        delay: float = 2.0,
    ) -> EvaluationResult:

        for attempt in range(max_retries):

            try:
                return self.evaluator.invoke(prompt)

            except Exception as e:

                # Retry only for rate-limit errors
                if "429" not in str(e):
                    raise

                # Exponential backoff
                wait_time = delay * (2 ** attempt)

                # Add small random jitter
                wait_time += random.uniform(0, 1)

                print(
                    f"Rate limit reached. "
                    f"Retrying in {wait_time:.2f} seconds..."
                )

                time.sleep(wait_time)

        raise RuntimeError(
            "Maximum retries exceeded because of rate limiting."
        )


    # =====================================================
    # Faithfulness
    # =====================================================

    def faithfulness(
        self,
        question: str,
        context: str,
        answer: str,
    ) -> EvaluationResult:
        """
        Evaluate whether the answer is supported
        by the retrieved context.
        """

        prompt = f"""
You are evaluating the faithfulness of an answer
generated by a Retrieval-Augmented Generation (RAG) system.

Your task is to determine whether the answer is fully
supported by the provided context.

Rules:
- Use ONLY the provided context.
- Do not use outside knowledge.
- Identify whether the claims in the answer
  are supported by the context.
- Penalize unsupported or invented claims.
- A fully supported answer should receive a score
  close to 1.0.
- An unsupported answer should receive a score
  close to 0.0.

Score the answer between 0 and 1.

Question:
{question}

Context:
{context}

Answer:
{answer}
"""

        return self._invoke_with_retry(prompt)


    # =====================================================
    # Answer Relevance
    # =====================================================

    def answer_relevance(
        self,
        question: str,
        answer: str,
    ) -> EvaluationResult:
        """
        Evaluate whether the generated answer
        directly answers the user's question.
        """

        prompt = f"""
You are evaluating the relevance of an answer
generated by a Retrieval-Augmented Generation (RAG) system.

Determine how well the answer addresses the user's question.

Rules:
- The answer should directly address the question.
- The answer should not contain unnecessary information.
- The answer should be clear and focused.
- Penalize answers that avoid the question.
- Penalize answers that discuss unrelated topics.
- A highly relevant answer should receive a score
  close to 1.0.
- An irrelevant answer should receive a score
  close to 0.0.

Score the answer between 0 and 1.

Question:
{question}

Answer:
{answer}
"""

        return self._invoke_with_retry(prompt)


    # =====================================================
    # Correctness
    # =====================================================

    def correctness(
        self,
        question: str,
        ground_truth: str,
        answer: str,
    ) -> EvaluationResult:
        """
        Evaluate whether the generated answer is
        correct compared with the ground truth.
        """

        prompt = f"""
You are evaluating the correctness of an answer
generated by a Retrieval-Augmented Generation (RAG) system.

Compare the generated answer with the provided ground truth.

Rules:
- Evaluate factual correctness.
- Check whether the important information in the
  ground truth is correctly reflected in the answer.
- Do not require the answer to use the exact wording
  of the ground truth.
- Different wording is acceptable if the meaning is correct.
- Penalize factual errors.
- Penalize contradictions with the ground truth.
- Penalize important missing information when it affects
  the correctness of the answer.
- A fully correct answer should receive a score
  close to 1.0.
- A completely incorrect answer should receive a score
  close to 0.0.

Score the answer between 0 and 1.

Question:
{question}

Ground Truth:
{ground_truth}

Generated Answer:
{answer}
"""

        return self._invoke_with_retry(prompt)


    # =====================================================
    # Calculate All Metrics
    # =====================================================

    def evaluate(
        self,
        question: str,
        context: str,
        ground_truth: str,
        answer: str,
    ) -> dict:
        """
        Calculate all generation metrics.
        """

        # ---------------------------------------------
        # Faithfulness
        # ---------------------------------------------

        faithfulness_result = self.faithfulness(
            question=question,
            context=context,
            answer=answer,
        )

        # Delay between API calls
        time.sleep(2)


        # ---------------------------------------------
        # Answer Relevance
        # ---------------------------------------------

        relevance_result = self.answer_relevance(
            question=question,
            answer=answer,
        )

        # Delay between API calls
        time.sleep(2)


        # ---------------------------------------------
        # Correctness
        # ---------------------------------------------

        correctness_result = self.correctness(
            question=question,
            ground_truth=ground_truth,
            answer=answer,
        )


        # ---------------------------------------------
        # Return Results
        # ---------------------------------------------

        return {
            "faithfulness": faithfulness_result.score,
            "answer_relevance": relevance_result.score,
            "correctness": correctness_result.score,

            "faithfulness_reason": faithfulness_result.reason,
            "answer_relevance_reason": relevance_result.reason,
            "correctness_reason": correctness_result.reason,
        }