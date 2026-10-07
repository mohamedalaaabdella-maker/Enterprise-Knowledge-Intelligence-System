import re

from langchain_core.documents import Document


def clean_text(text: str) -> str:
    """
    Clean Markdown text while preserving its original structure
    and technical content.
    """

    # --------------------------------------------------
    # 1. Normalize line endings
    # --------------------------------------------------

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # --------------------------------------------------
    # 2. Remove trailing whitespace from each line
    # --------------------------------------------------

    text = "\n".join(
        line.rstrip()
        for line in text.split("\n")
    )

    # --------------------------------------------------
    # 3. Remove excessive blank lines
    # --------------------------------------------------

    text = re.sub(r"\n{3,}", "\n\n", text)

    # --------------------------------------------------
    # 4. Remove leading/trailing whitespace
    # --------------------------------------------------

    text = text.strip()

    return text


def clean_documents(documents: list[Document]) -> list[Document]:
    """
    Clean all documents while preserving their metadata.
    """

    cleaned_documents = []

    for document in documents:

        cleaned_content = clean_text(document.page_content)

        cleaned_document = Document(
            page_content=cleaned_content,
            metadata=document.metadata.copy(),
        )

        cleaned_documents.append(cleaned_document)

    return cleaned_documents