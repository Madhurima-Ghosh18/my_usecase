import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer
from config import Config

class EmbeddingService:
    """
    Vector search using FAISS + sentence-transformers.
    Pure Python — no DLL, no server, works on Windows perfectly.
    Saves index and metadata to disk so data persists between runs.
    """

    def __init__(self):
        self.model      = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.index_path = os.path.join(Config.FAISS_DB_PATH, 'faiss.index')
        self.meta_path  = os.path.join(Config.FAISS_DB_PATH, 'metadata.json')
        self.index      = None
        self.metadata   = []  # stores runbook info alongside each vector

        os.makedirs(Config.FAISS_DB_PATH, exist_ok=True)
        self._load_if_exists()

    def _load_if_exists(self):
        """Load existing index from disk if it exists"""
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, 'r') as f:
                self.metadata = json.load(f)
            print(f"Loaded FAISS index with {self.index.ntotal} runbooks")

    def index_runbooks(self, runbooks):
        documents = []
        self.metadata = []

        for runbook in runbooks:
            embed_text = f"""
                Title: {runbook['title']}
                Category: {runbook['category']}
                Keywords: {runbook['keywords']}
                Steps overview: {runbook['steps'][:500]}
            """.strip()

            documents.append(embed_text)
            self.metadata.append({
                'runbook_id': str(runbook['id']),
                'title':      runbook['title'],
                'category':   runbook['category']
            })

        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.model.encode(documents, convert_to_numpy=True)
        embeddings = embeddings.astype(np.float32)

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        # Build FAISS index
        dimension  = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product = cosine after normalize
        self.index.add(embeddings)

        # Save to disk
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'w') as f:
            json.dump(self.metadata, f)

        print(f"✅ Indexed {len(runbooks)} runbooks into FAISS")

    def search(self, query_text, n_results=3):
        """
        Semantic search — finds most similar runbooks to query.
        Returns list of dicts with runbook_id, title, similarity_score.
        """
        if self.index is None or self.index.ntotal == 0:
            print("FAISS index is empty. Run setup_faiss.py first.")
            return []

        # Embed the query
        query_vec = self.model.encode([query_text], convert_to_numpy=True)
        query_vec = query_vec.astype(np.float32)
        faiss.normalize_L2(query_vec)

        # Search
        k       = min(n_results, self.index.ntotal)
        scores, indices = self.index.search(query_vec, k)

        matches = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            similarity = float(score)  # already cosine similarity after normalize
            if similarity >= Config.SIMILARITY_THRESHOLD:
                meta = self.metadata[idx]
                matches.append({
                    'runbook_id':       int(meta['runbook_id']),
                    'title':            meta['title'],
                    'category':         meta['category'],
                    'similarity_score': round(similarity, 4)
                })

        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches

    def get_collection_count(self):
        return self.index.ntotal if self.index else 0