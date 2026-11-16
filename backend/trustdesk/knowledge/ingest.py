"""Load a folder of policy documents and turn them into chunks."""

from pathlib import Path

from trustdesk.knowledge.chunking import Chunk, chunk_text

SUPPORTED_SUFFIXES = {".txt", ".md"}


def load_policies(directory: Path | str) -> list[Chunk]:
    """Chunk every .txt/.md file under `directory` (sub-folders included), in a stable order."""
    root = Path(directory)
    if not root.is_dir():
        raise FileNotFoundError(f"policy folder not found: {root}")
    chunks = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            source = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8-sig")
            chunks.extend(Chunk(source, piece) for piece in chunk_text(text))
    return chunks
