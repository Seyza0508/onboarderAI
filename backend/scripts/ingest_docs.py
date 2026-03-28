import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rag.ingestion import RAG_INDEX_PATH, build_index


def main() -> None:
    path = build_index(force_rebuild=True)
    print(f"RAG index built at {path}")
    print(f"RAG index exists: {RAG_INDEX_PATH.exists()}")


if __name__ == "__main__":
    main()
