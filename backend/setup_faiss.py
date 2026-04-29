from models.runbook_model import RunbookModel
from services.embedding_service import EmbeddingService

def setup_faiss():
    print("Setting up FAISS vector store...")

    # Get all runbooks from SQLite
    model    = RunbookModel()
    runbooks = model.get_all_runbooks()

    if not runbooks:
        print("❌ No runbooks found in SQLite. Run setup_sqlite.py first.")
        return

    print(f"Found {len(runbooks)} runbooks in SQLite")

    # Embed and store in FAISS
    embedding_service = EmbeddingService()
    embedding_service.index_runbooks(runbooks)

    # Verify
    count = embedding_service.get_collection_count()
    print(f"✅ FAISS setup complete. {count} runbooks indexed.")
    print(f"📁 Index saved at: {embedding_service.index_path}")
    print(f"📁 Metadata saved at: {embedding_service.meta_path}")

    # Quick test search
    print("\nRunning test search: 'postgres database connection error'")
    results = embedding_service.search("postgres database connection error")
    if results:
        for r in results:
            print(f"  → {r['title']} (similarity: {r['similarity_score']})")
    else:
        print("  No results above similarity threshold")

    print("\nRunning test search: 'server running slow high cpu'")
    results = embedding_service.search("server running slow high cpu")
    if results:
        for r in results:
            print(f"  → {r['title']} (similarity: {r['similarity_score']})")
    else:
        print("  No results above similarity threshold")

if __name__ == "__main__":
    setup_faiss()