from pydantic import BaseModel , Field
from langchain_core.documents import Document
from src.generation.llm import create_llm
from src.generation.prompt import RELEVANCE_PROMPT

class RelevanceResult(BaseModel):
    relevant: bool = Field(
        description="Whether the retrieved documents are relevant to the user's question."
    )

def create_relevance_checker():
    llm = create_llm()

    structured_llm = llm.with_structured_output(
        RelevanceResult
    )

    relevance_checker = RELEVANCE_PROMPT | structured_llm

    return relevance_checker


def check_relevance(
    relevance_checker,
    question: str,
    documents: list[Document],
) -> bool:

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    result = relevance_checker.invoke(
        {
            "question": question,
            "context": context,
        }
    )

    return result.relevant