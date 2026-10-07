from src.config import CHUNK_OVERLAP , CHUNK_SIZE
from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter
)

# ==================================================
# Chunking Configuration
# ==================================================



markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ],
    strip_headers=False,
)

character_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
)

def chunk_document(document: Document) -> list[Document]:
    """
    Split one cleaned Markdown document into
    structure-aware chunks.
    """

    sections = markdown_splitter.split_text(
        document.page_content
    )

    chunks = []

    # Chunk counter for this document
    chunk_index = 0

    # ----------------------------------------------
    # Step 2: Process each section
    # ----------------------------------------------

    for section in sections:

        # Preserve original document metadata
        metadata = document.metadata.copy()

        # Add section metadata extracted from Markdown
        metadata.update(section.metadata)

        if len(section.page_content) <= CHUNK_SIZE:

            metadata["chunk_id"] = (
                f"{document.metadata['document_id']}_{chunk_index:03d}"
            )

            chunks.append(
                Document(
                    page_content=section.page_content,
                    metadata=metadata,
                )
            )

            chunk_index += 1

        else:

            # --------------------------------------
            # Step 4: Split large sections
            # --------------------------------------

            sub_chunks = character_splitter.split_text(
                section.page_content
            )

            for sub_chunk in sub_chunks:

                sub_metadata = metadata.copy()

                sub_metadata["chunk_id"] = (
                    f"{document.metadata['document_id']}_{chunk_index:03d}"
                )

                chunks.append(
                    Document(
                        page_content=sub_chunk,
                        metadata=sub_metadata,
                    )
                )

                chunk_index += 1

    return chunks


def chunk_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Chunk all cleaned documents while preserving
    document and section metadata.
    """

    all_chunks = []

    for document in documents:

        document_chunks = chunk_document(document)

        all_chunks.extend(document_chunks)

    return all_chunks

