# agents/search_agent.py
from services.embedding_service import EmbeddingService
from models.runbook_model import RunbookModel
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import HuggingFaceEndpoint
from config import Config

class SearchAgent:
    

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.runbook_model     = RunbookModel()

    def run(self, ticket):
        """
        Main entry point.
        Input:  ticket dict { summary, description, key }
        Output: dict {
                    match_type: 'single' | 'multiple' | 'no_match',
                    matched_runbooks: [ full runbook dicts ],
                    ticket_context: original ticket
                }
        """
        print(f"\n[Agent 1] Running semantic search for ticket: {ticket['key']}")

        # Combine ticket text for embedding
        query_text = f"{ticket['summary']} {ticket['description']}"

        # Search FaissStore for similar runbooks
        search_results = self.embedding_service.search(query_text, n_results=3)

        if not search_results:
            print("[Agent 1] No matches found above similarity threshold")
            return {
                'match_type':      'no_match',
                'matched_runbooks': [],
                'ticket_context':   ticket
            }

        # Fetch full runbook data from SQLite using the IDs from FaissDB
        matched_runbooks = []
        for result in search_results:
            full_runbook = self.runbook_model.get_runbook_by_id(result['runbook_id'])
            if full_runbook:
                # Attach the similarity score from FaissDB
                full_runbook['similarity_score'] = result['similarity_score']
                full_runbook['confidence']        = round(result['similarity_score'] * 100, 1)
                matched_runbooks.append(full_runbook)

        # Decide match type
        if len(matched_runbooks) == 1:
            match_type = 'single'
        else:
            match_type = 'multiple'

        print(f"[Agent 1] Found {len(matched_runbooks)} match(es): "
              f"{[rb['title'] for rb in matched_runbooks]}")

        return {
            'match_type':       match_type,
            'matched_runbooks': matched_runbooks,
            'ticket_context':   ticket
        }