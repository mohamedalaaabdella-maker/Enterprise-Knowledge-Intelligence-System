from langchain_openai import ChatOpenAI
from src.config import LLM_API_KEY , LLM_BASE_URL , LLM_MODEL

def create_llm() -> ChatOpenAI:

    """
    Create the LLM used for query rewriting
    and answer generation.
    """

    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0,
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL
    )

    return llm
