from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from src.ingestion.loaders import load_documents
from src.ingestion.cleaner import clean_documents
from src.ingestion.chunker import chunk_documents
from src.retrieval.dense import (
    create_embedding_model , 
    create_vector_store,
    load_vector_store
)
from src.retrieval.bm25 import (
    create_bm25_index
)
from src.retrieval.hybrid import hybrid_search
from src.retrieval.reranker import (
    create_reranker ,
    rerank_documents
)

from src.generation.llm import create_llm
from src.generation.relevance import(
    create_relevance_checker,
    check_relevance
)
from src.generation.generator import (
    create_generator,
    generate_answer
)

from src.generation.prompt import QUERY_REWRITE_PROMPT



class RAGServices:
    """
    Main service container for the Enterprise RAG system.

    This class initializes and coordinates:
    - Document ingestion
    - Chunking
    - Vector store
    - BM25
    - Hybrid retrieval
    - Reranking
    - Query rewriting
    - Relevance checking
    - Grounded generation
    """

    def __init__(self):

        # -----------------------------------------
        # Retrieval components
        # -----------------------------------------

        self.embedding = create_embedding_model()
        self.vector_store = load_vector_store(self.embedding)

        # Load and prepare documents for BM25
        documents = load_documents()
        cleaned_documents = clean_documents(documents)
        self.chunks = chunk_documents(cleaned_documents)

        self.bm25 = create_bm25_index(self.chunks)


        # -----------------------------------------
        # Reranker
        # -----------------------------------------

        self.reranker = create_reranker()

        # -----------------------------------------
        # Generation components
        # -----------------------------------------

        self.llm = create_llm()
        self.relevance_checker = create_relevance_checker()
        self.generator = create_generator()
        self.query_rewriter = (
            QUERY_REWRITE_PROMPT | self.llm | StrOutputParser()
        )

    # =================================================
    # Query Rewriting
    # =================================================

    def rewrite_query(
        self,
        question: str,
    ) -> str:
        """
        Rewrite the user's question into a
        retrieval-friendly search query.
        """
        response = self.query_rewriter.invoke(
            {
                "question": question
            }
        )

        return response

    # =================================================
    # Retrieval
    # =================================================

    def retrieve(
        self,
        query: str,
        dense_k: int = 20,
        bm25_k: int = 20,
        final_k: int = 20,
    ) -> list[Document]:
        """
        Retrieve candidate documents using
        hybrid retrieval.
        """

        documents = hybrid_search(
            query=query,
            vector_store=self.vector_store,
            bm25=self.bm25,
            chunks=self.chunks,
            dense_k=dense_k,
            bm25_k=bm25_k,
            final_k=final_k,
        )

        return documents

    # =================================================
    # Reranking
    # =================================================

    def rerank(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 10,
    ) -> list[Document]:
        """
        Rerank retrieved documents using the
        Cross-Encoder reranker.
        """

        return rerank_documents(
            reranker=self.reranker,
            query=query,
            documents=documents,
            top_k=top_k
        )


    # =================================================
    # Relevance Check
    # =================================================

    def check_relevance(
        self,
        question: str,
        documents: list[Document],
    ) -> bool:
        """
        Check whether retrieved documents contain
        enough relevant information.
        """

        return check_relevance(
            relevance_checker=self.relevance_checker,
            question=question,
            documents=documents,
        )   

    # =================================================
    # Generation
    # =================================================

    def generate(
        self,
        question: str,
        documents: list[Document],
    ) -> str:
        """
        Generate a grounded answer using
        the retrieved documents.
        """

        return generate_answer(
            generator=self.generator,
            question=question,
            documents=documents,
        )


    # =================================================
    # Main RAG Pipeline
    # =================================================

    def ask(
        self,
        question: str,
        retrieval_k: int = 20,
        rerank_k: int = 5,
        max_rewrites: int = 1,
    ) -> dict:
        """
        Run the complete RAG pipeline.

        Flow:

        Question
            ↓
        Hybrid Retrieval
            ↓
        Reranking
            ↓
        Relevance Check
            ↓
        ┌───────────────┐
        │ Relevant?     │
        └───────────────┘
          ↓ Yes     ↓ No
        Generate   Rewrite
                       ↓
                    Retrieve
                       ↓
                    Rerank
                       ↓
                 Relevance Check
                       ↓
                    Generate
        """

        original_question = question
        current_question = question

        rewrite_count = 0

        while True:

            # -----------------------------------------
            # 1. Hybrid Retrieval
            # -----------------------------------------

            retrieved_documents = self.retrieve(
                query=current_question,
                final_k=retrieval_k,
            )

            # -----------------------------------------
            # 2. Reranking
            # -----------------------------------------

            reranked_documents = self.rerank(
                query=current_question,
                documents=retrieved_documents,
                top_k=rerank_k,
            )

            # -----------------------------------------
            # 3. Relevance Check
            # -----------------------------------------

            relevant = self.check_relevance(
                question=original_question,
                documents=reranked_documents,
            )


            # -----------------------------------------
            # 4. If relevant → Generate
            # -----------------------------------------

            if relevant:
                answer = self.generate(
                    question=original_question,
                    documents=reranked_documents,
                )

                return {
                    "question": original_question,
                    "query_used": current_question,
                    "rewritten": rewrite_count > 0,
                    "rewrite_count": rewrite_count,
                    "relevant": True,
                    "documents": reranked_documents,
                    "answer": answer,
                }


            # -----------------------------------------
            # 5. If not relevant → Rewrite
            # -----------------------------------------

            if rewrite_count >= max_rewrites:
                return {
                    "question": original_question,
                    "query_used": current_question,
                    "rewritten": rewrite_count > 0,
                    "rewrite_count": rewrite_count,
                    "relevant": False,
                    "documents": reranked_documents,
                    "answer": (
                        "There is not enough relevant "
                        "information in the retrieved "
                        "context to answer this question."
                    ),
                }

            current_question = self.rewrite_query(
                original_question
            )

            rewrite_count += 1
