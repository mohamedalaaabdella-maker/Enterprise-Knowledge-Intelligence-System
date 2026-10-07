from langchain_core.documents import Document
from src.generation.llm import create_llm
from src.generation.prompt import ANSWER_PROMPT
from langchain_core.output_parsers import StrOutputParser

def create_generator():
    """
    Create the LLM chain used for grounded answer generation.
    """

    llm = create_llm()

    generator = ANSWER_PROMPT | llm | StrOutputParser()

    return generator

def format_context(documents: list[Document]) -> str:
    """
    Combine retrieved documents into a single context string.
    """

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    return context


def generate_answer(
    generator,
    question: str,
    documents: list[Document],
) -> str:
    """
    Generate an answer using only the retrieved documents.
    """

    context = format_context(documents)

    response = generator.invoke(
        {
            "question": question,
            "context": context,
        }
    )

    return response