"""Document loading utilities."""
import json
from pathlib import Path

from langchain_core.documents import Document

from src.config import DOCUMENTS_DIR , METADATA_FILE

def load_metadata(metadata_file: Path = METADATA_FILE) -> list[dict]:
    """
    Load document metadata from metadata.json.
    """

    with metadata_file.open('r' , encoding='utf-8') as file :
        metadata = json.load(file)

    return metadata


def load_markdown_file(file_path: str | Path) -> str:
    """
    Read a Markdown file and return its text content.
    """

    file_path = Path(file_path)

    return file_path.read_text(encoding="utf-8")


def load_documents(
    documents_dir: Path = DOCUMENTS_DIR,
    metadata_file: Path = METADATA_FILE,
) -> list[Document]:
    """
    Load all Markdown documents and attach their metadata.
    """

    metadata_list = load_metadata(metadata_file)

    documents = []

    # Find all Markdown files recursively
    markdown_files = sorted(documents_dir.rglob("*.md"))

    for file_path in markdown_files:

        # Convert absolute path to path relative to data/documents/
        relative_path = file_path.relative_to(documents_dir)

        # Find metadata for this document
        matching_metadata = None

        for metadata in metadata_list:
            if metadata["file_path"] == relative_path.as_posix():
                matching_metadata = metadata
                break

        if matching_metadata is None:
            print(f"Warning: No metadata found for {relative_path}")
            continue

        # Read document content
        content = load_markdown_file(file_path)

        # Create structured Document
        document = Document(
            page_content=content,
            metadata=matching_metadata,
        )

        documents.append(document)

    return documents


